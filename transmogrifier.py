import argparse
import datetime
import json
import logging
import pathlib
import sys


handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def load_set_and_card_info(filename):
    with open(filename) as fp:
        return json.load(fp)


def aggregate_cards_from_decklists(filename):
    with open(filename) as fp:
        all_decklists = json.load(fp)

    card_aggregate = {}

    for decklist in all_decklists:
        for name, count in decklist.items():
            name = name.lower()
            if name in card_aggregate:
                card_aggregate[name] += count
            else:
                card_aggregate[name] = count

    return card_aggregate


def save_set_to_file(set_code, cards, out_dir):
    path = pathlib.Path("./{}/sets/".format(out_dir))
    path.mkdir(parents=True, exist_ok=True)
    with open("{}/{}.json".format(path.absolute(), set_code), "w") as fp:
        json.dump(cards, fp)


def save_set_meta_file(set_meta, out_dir):
    path = pathlib.Path("./{}/".format(out_dir))
    path.mkdir(parents=True, exist_ok=True)
    with open("{}/sets.json".format(path.absolute()), "w") as fp:
        json.dump(set_meta, fp)


def transmogrify(all_set_data_file, scrapped_data_file, out_dir):
    set_and_cards = load_set_and_card_info(all_set_data_file)
    card_aggregate = aggregate_cards_from_decklists(scrapped_data_file)

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
            save_set_to_file(
                set_code=set_data["code"], cards=cards_in_set, out_dir=out_dir
            )
            logger.info('Saved {} set with {} cards in set'.format(set_data['code'], len(cards_in_set)))
        else:
            logger.info('Skipped {} due to no cards played'.format(set_data['code']))

        sets_meta.append(
            {
                "code": set_data["code"],
                "name": set_data["name"],
                "releaseDate": set_data["releaseDate"],
                "count": len(cards_in_set),
            }
        )

    sets_meta.sort(reverse=True, key=lambda s: datetime.datetime.fromisoformat(s['releaseDate']).timestamp())
    save_set_meta_file(set_meta=sets_meta, out_dir=out_dir)


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]",
        description="Prepare most played cards per set for input data.",
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
        default="scrapped_data.json",
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
    logger.info('Starting transmogrification')
    transmogrify(
        all_set_data_file=args.all_card_data,
        scrapped_data_file=args.scrapped_data,
        out_dir=args.out_dir,
    )
    logger.info('Done, output in {}'.format(args.out_dir))


if __name__ == "__main__":
    main()
