import sys
import os
import click

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from paperl import *
from search_embedding import label_paper_by_oag


@click.command()
@click.option("--way", default='oag_bert',
              help="you can choose the way to label papaers that you can choose oag_bert or strong_match")
def main(way: str):
    if way == "oag_bert":
        label_paper_by_oag()
    else:
        label_paper_by_strong_match()


if __name__ == "__main__":
    main()
