import os

import transmogrifier
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface


class PrepareForVisualizerPipeline(object):
    def __init__(self):
        self.items = []

    def process_item(self, item, spider):
        self.items.append(item)
        return item

    def close_spider(self, spider):
        transmogrifier.clear_output_folder(
            out_dir=spider.out_dir,
            mtg_format=spider.mtg_format,
        )
        spider.logger.info("Aggregating results...")
        transmogrifier.transmogrify(
            all_set_data_file=spider.all_set_data_file,
            out_dir=spider.out_dir,
            mtg_format=spider.mtg_format,
            items=self.items,
        )
        os.rename('tmp-scrapped-data.json', '{}-scrapped-data.json'.format(spider.mtg_format))
