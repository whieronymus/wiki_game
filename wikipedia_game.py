import argparse
from copy import copy
from typing import List, Optional

from wiki_api import clean_title
from wiki_db import Page


class LinkMap:
    """
    LinkMap objects collect links starting from the source or the
    target. They are used to determine if one of the links from the
    source has mapped to one of the backlinks from the target.

    When a match is found, the are passed into get_path to genrate
    the programs completion output.
    """
    def __init__(self, end: Page, existing_map: Optional[List[Page]] = None):
        if existing_map is not None:
            self.map = list(existing_map)
        else:
            try:
                self.map = [end]
            except:
                Exception("Oh boy")

    def __len__(self):
        return len(self.map)

    def add_next(self, next_p: Page):
        self.map.append(next_p)
        return self

    def current(self):
        return self.map[-1]

    def reverse_map(self):
        return [p for p in self.map][::-1]

    def __eq__(self, other):
        return self.current().title == other.current().title

    def __hash__(self):
        return hash((self.current().title, len(self)))

    def __copy__(self):
        return LinkMap(end=self.map[0], existing_map=self.map)


def get_path(source_map: LinkMap, target_map: LinkMap) -> str:
    """
    Returns the path from source to target given two LinkMaps
    """
    return " -> ".join([p.title for p in source_map.map + target_map.reverse_map()])


def map_source_to_target(source: Page, target: Page) -> str:
    """
    Given a starting page on Wikipedia, using connected pages,
    finds a list of linked pages to a target page.
    """
    source_maps = [LinkMap(source).add_next(l) for l in source.get_links()]
    target_maps = [LinkMap(target).add_next(bl) for bl in target.get_backlinks()]

    current_targets = set([LinkMap(target)] + target_maps)
    source_maps = set([LinkMap(source)] + source_maps)

    round = 1
    while True:
        print("depth", round)
        print(len(current_targets))
        print(len(source_maps))
        for sm in source_maps:
            if sm in current_targets:
                # If SM in current_targets we found our target and we can
                # reconstruct our map
                targets_sorted = sorted(current_targets, key=lambda x: len(x))
                return get_path(sm, targets_sorted[0])

        # Else we go out to all our current pages, and the next roudn of links for them.
        ct_update = []
        for ct in current_targets:
            ct_update.extend([copy(ct).add_next(l) for l in ct.current().get_backlinks()])
        current_targets.update(ct_update)
        sm_update = []
        for sm in source_maps:
            sm_update.extend([copy(sm).add_next(l) for l in sm.current().get_links()])
        source_maps.update(sm_update)

        round += 1


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "source",
        help="This is the starter page the program will start from."
    )
    parser.add_argument(
        "target",
        help="This is the target page the program will try to locate."
    )
    args = parser.parse_args()

    source = Page.get_or_create(clean_title(args.source))
    target = Page.get_or_create(clean_title(args.target))
    # source = Page.get_or_create("Hellenic_historiography")
    # target = Page.get_or_create("Cholistan_Desert")

    print(map_source_to_target(source, target))


if __name__ == "__main__":
    main()