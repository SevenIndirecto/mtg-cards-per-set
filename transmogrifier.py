import argparse
import datetime
import json
import logging
import pathlib
import shutil
import sys


handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def _load_set_and_card_info(filename):
    with open(filename) as fp:
        return json.load(fp)


def _aggregate_cards_from_decklists(all_decklists):
    card_aggregate = {}

    for decklist in all_decklists:
        for name, count in decklist.items():
            name = name.lower()
            if name in card_aggregate:
                card_aggregate[name] += count
            else:
                card_aggregate[name] = count

    return card_aggregate


def _save_set_to_file(set_code, cards, out_dir, mtg_format):
    path = pathlib.Path("./{}/{}/".format(out_dir, mtg_format))
    path.mkdir(parents=True, exist_ok=True)
    with open("{}/{}.json".format(path.absolute(), set_code), "w") as fp:
        json.dump(cards, fp)


def _save_set_meta_file(set_meta, out_dir):
    path = pathlib.Path("./{}/".format(out_dir))
    path.mkdir(parents=True, exist_ok=True)
    with open("{}/sets.json".format(path.absolute()), "w") as fp:
        json.dump(set_meta, fp)


def clear_output_folder(out_dir, mtg_format):
    path = pathlib.Path("./{}/{}".format(out_dir, mtg_format))
    try:
        shutil.rmtree(path)
        logger.info('Deleted old data for [{}] format'.format(mtg_format))
    except FileNotFoundError:
        pass


def transmogrify(all_set_data_file, out_dir, scrapped_data_file='', mtg_format='modern', items=None):
    """
    :param all_set_data_file:
    :param out_dir:
    :param scrapped_data_file:
    :param mtg_format:
    :param items: If a list of decklist dicts is provided, no need to read from scrapped_data_file
    :return:
    """
    set_and_cards = _load_set_and_card_info(all_set_data_file)

    if items is None:
        with open(scrapped_data_file) as fp:
            items = json.load(fp)
    card_aggregate = _aggregate_cards_from_decklists(items)

    sets_meta = []

    # Create one json file for each Set
    for set_data in set_and_cards["data"].values():
        cards_added = set()
        cards_in_set = []
        for card in set_data["cards"]:
            card_name_lower = card["name"].lower()

            if card_name_lower not in card_aggregate or card_name_lower in cards_added:
                continue

            cards_added.add(card_name_lower)
            cards_in_set.append(
                {
                    "name": card["name"],
                    "scryfallId": card["identifiers"]["scryfallId"],
                    "count": card_aggregate[card_name_lower],
                }
            )

        cards_in_set.sort(reverse=True, key=lambda c: c["count"])
        if len(cards_in_set) > 0:
            _save_set_to_file(
                set_code=set_data["code"], cards=cards_in_set, out_dir=out_dir, mtg_format=mtg_format
            )
            logger.info(
                "Saved {} set with {} cards in set".format(
                    set_data["code"], len(cards_in_set)
                )
            )
        else:
            logger.info("Skipped {} due to no cards played".format(set_data["code"]))

        sets_meta.append(
            {
                "code": set_data["code"],
                "name": set_data["name"],
                "releaseDate": set_data["releaseDate"],
            }
        )

    sets_meta.sort(
        reverse=True,
        key=lambda s: datetime.datetime.fromisoformat(s["releaseDate"]).timestamp(),
    )
    _save_set_meta_file(set_meta=sets_meta, out_dir=out_dir)


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]",
        description="Prepare most played cards per set for input data.",
    )
    parser.add_argument(
        "-f",
        "--mtg_format",
        type=str,
        default="modern",
    )
    parser.add_argument(
        "-a",
        "--all_card_data",
        type=str,
        default="alldata.json",
    )
    parser.add_argument(
        "-s",
        "--scrapped_data",
        type=str,
        default="tmp-scrapped-data.json",
    )
    parser.add_argument(
        "-o",
        "--out_dir",
        type=str,
        default="visualizer/output_data",
    )
    return parser


def main():
    parser = init_argparse()
    args = parser.parse_args()
    logger.info("Starting transmogrification for {}".format(args.mtg_format))
    clear_output_folder(out_dir=args.out_dir, mtg_format=args.mtg_format)
    transmogrify(
        all_set_data_file=args.all_card_data,
        out_dir=args.out_dir,
        scrapped_data_file=args.scrapped_data,
        mtg_format=args.mtg_format,
    )
    logger.info("Done, output in {}".format(args.out_dir))


if __name__ == "__main__":
    main()
