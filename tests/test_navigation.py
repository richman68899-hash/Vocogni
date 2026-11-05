"""Regression tests for learner-first primary navigation."""

from app import NAV_ITEMS


def test_learn_is_the_first_primary_navigation_destination():
    assert NAV_ITEMS[0] == ("Learn", "Browse")


def test_supporting_destinations_follow_the_learning_entry_point():
    labels = [label for label, _route in NAV_ITEMS]
    assert labels == ["Learn", "Progress", "Notes", "Profile", "Settings"]


def test_navigation_routes_are_unique():
    routes = [route for _label, route in NAV_ITEMS]
    assert len(routes) == len(set(routes))
