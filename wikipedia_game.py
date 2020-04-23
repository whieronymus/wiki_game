import argparse
import requests
from typing import List, Optional
from copy import copy
from queue import Queue

from wiki_api import clean_title
from wiki_db import Page


class LinkMap:
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
    Returns the path from source to target
    """
    print()
    m1 = source_map.map
    m2 = target_map.reverse_map()
    f = m1 + m2
    print()
    return " -> ".join([p.title for p in source_map.map + target_map.reverse_map()])


def map_source_to_target(source: Page, target: Page) -> str:
    """
    Given a starting page on Wikipedia, using connected pages,
    finds a list of linked pages to a target page.
    """
    source_maps = [LinkMap(source).add_next(l) for l in source.get_links()]
    target_maps = [LinkMap(target).add_next(bl) for bl in target.get_backlinks()]

    searching_for_target = True
    current_targets = set([LinkMap(target)] + target_maps)
    source_maps = set([LinkMap(source)] + source_maps)
    round = 1
    while searching_for_target:
        print("depth", round)
        print(len(current_targets))
        print(len(source_maps))
        for sm in source_maps:
            if sm in current_targets:
                # If SM in current_targets we found our target and we can
                # reconstruct our map
                targets_sorted = sorted(current_targets, key=lambda x: len(x))
                return get_path(sm, targets_sorted[0])

        ct_update = []
        for ct in current_targets:
            ct_update.extend([copy(ct).add_next(l) for l in ct.current().get_backlinks()])
        current_targets.update(ct_update)
        sm_update = []
        for sm in source_maps:
            sm_update.extend([sm.copy().add_next(l) for l in sm.current().get_links()])
        source_maps.update(sm_update)

        round += 1


# def also_linked_from_target(target: Page) -> None:
#     target_links = target.get_links()
#     num_target_backlinks = len(target_links)
#     num_target_backlinks_also_linked_to_target = 0
#
#     print(num_target_backlinks)
#     for link in target_links:
#         targets_backlinks_links = link.get_links()
#         if target in set(targets_backlinks_links):
#             print(link.title)
#             num_target_backlinks_also_linked_to_target += 1
#
#     print(f"{num_target_backlinks_also_linked_to_target} of {num_target_backlinks}")
#     print(f"{(num_target_backlinks_also_linked_to_target / num_target_backlinks) * 100}%")
#
#
# def check_back_links(target: Page) -> None:
#     target_backlinks = target.get_backlinks()
#     num_target_backlinks = len(target_backlinks)
#     num_backlinks_linked_to_target = 0
#     print(num_target_backlinks)
#     for link in target_backlinks:
#         targets_link_links = link.get_links()
#         if target in set(targets_link_links):
#             print(link.title)
#             num_backlinks_linked_to_target += 1
#
#     print(f"{num_backlinks_linked_to_target} of {num_target_backlinks}")
#     print(f"{(num_backlinks_linked_to_target / num_target_backlinks) * 100}%")


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
    source = Page.get_or_create("Hellenic_historiography")
    target = Page.get_or_create("Cholistan_Desert")

    print(map_source_to_target(source, target))


if __name__ == "__main__":
    main()