"""Streamlit presentation for Streak Garden inside Learning Rhythm."""
from __future__ import annotations

from datetime import datetime

import streamlit as st

import data
import learning_maintenance
import state
from . import engine
from .enums import GrowthStage
from .models import default_garden_state
from .rules import tree_sale_value


_STAGE_ART = {
    GrowthStage.SEEDLING: "🌱",
    GrowthStage.SAPLING: "🌿",
    GrowthStage.MATURE: "🌳",
}


def _course_names() -> dict[str, str]:
    names = {}
    for course_id in data.COURSE_ORDER:
        course = data.get_course(course_id)
        if isinstance(course, dict):
            names[course_id] = str(
                course.get("title") or course.get("topic_label") or course_id
            )
    return names


def _render_forest(forest: dict, garden_state: dict, today) -> None:
    with st.container(border=True):
        heading, count = st.columns([4, 1])
        with heading:
            st.markdown(f"**{forest['name']} Forest**")
            st.caption(
                f"{forest['qualifying_days']} / {forest['target_days']} learning days "
                f"this cycle · {forest['percentage']}% grassland"
            )
        with count:
            st.metric("Trees", f"{forest['active_tree_count']}/{forest['tree_capacity']}")

        st.progress(int(forest["percentage"]))
        slots = st.columns(5)
        active_trees = list(forest["active_trees"])
        for index in range(int(forest["tree_capacity"])):
            with slots[index % len(slots)]:
                if index < len(active_trees):
                    stage = GrowthStage(int(active_trees[index]["growth_stage"]))
                    st.markdown(
                        f"<div style='text-align:center;font-size:1.75rem'>{_STAGE_ART[stage]}</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "<div style='text-align:center;color:#9ca3af;font-size:1.75rem'>·</div>",
                        unsafe_allow_html=True,
                    )

        if forest["is_full"]:
            st.caption("Forest complete. Sell a tree to open a new slot.")
        elif forest["current_cycle_tree_exists"]:
            st.caption("This milestone has planted a tree. Further learning days grow it.")
        elif forest["qualifying_days"] >= forest["target_days"]:
            st.caption("Milestone reached. A tree is waiting for an available forest slot.")
        else:
            remaining = max(0, forest["target_days"] - forest["qualifying_days"])
            st.caption(
                f"{remaining} more qualifying learning "
                f"{'day' if remaining == 1 else 'days'} to plant a tree."
            )

        with st.expander("Tree collection and management"):
            if not active_trees and not forest["sold_trees"]:
                st.caption("Your first tree appears when you complete a milestone.")
            for tree in active_trees:
                stage = GrowthStage(int(tree["growth_stage"]))
                left, right = st.columns([3, 1.5])
                with left:
                    st.write(f"{_STAGE_ART[stage]} {stage.name.title()} · {tree['cycle_start']}")
                with right:
                    value = tree_sale_value(tree["growth_stage"])
                    if st.button(
                        f"Sell · {value} Dew",
                        key=f"streak_garden_sell_{tree['id']}",
                        use_container_width=True,
                    ):
                        updated, paid = engine.sell_tree(garden_state, tree["id"], today)
                        st.session_state.streak_garden = updated
                        state.mark_persistent_dirty()
                        st.toast(f"Tree sold · +{paid} Dew")
                        st.rerun()

            if forest["sold_trees"]:
                sold_count = len(forest["sold_trees"])
                st.caption(
                    f"{sold_count} previously sold "
                    f"{'tree' if sold_count == 1 else 'trees'} remain in your achievement history."
                )


def render(progress: dict, profile: dict) -> None:
    """Render Streak Garden and persist only actual progression changes."""
    timezone_label = (
        profile.get("timezone", "Prefer not to say")
        if isinstance(profile, dict)
        else "Prefer not to say"
    )
    local_timezone = learning_maintenance.timezone_from_profile(timezone_label)
    today = datetime.now(local_timezone).date()

    course_names = _course_names()
    active_by_course = learning_maintenance.activity_dates_by_course(
        progress, timezone_label
    )
    all_active_dates = learning_maintenance.activity_dates(progress, timezone_label)

    current_state = st.session_state.get("streak_garden", default_garden_state())
    updated_state, changed = engine.synchronize_garden(
        current_state, course_names, active_by_course, all_active_dates, today
    )
    st.session_state.streak_garden = updated_state
    if changed:
        state.mark_persistent_dirty()

    summary = engine.garden_summary(
        updated_state, active_by_course, all_active_dates, today
    )

    st.markdown("#### Streak Garden")
    st.caption(
        "Meaningful learning adds water to your garden. Five learning days in a "
        "seven-day forest cycle plant a tree; further days grow it."
    )
    wallet_col, trees_col = st.columns(2)
    with wallet_col:
        st.metric("Dew", summary["dew_balance"], help="Earn Dew through learning and milestone growth.")
    with trees_col:
        total_trees = sum(forest["active_tree_count"] for forest in summary["forests"])
        st.metric("Growing trees", total_trees)

    if not summary["forests"]:
        st.info("Your course forests will appear here.")
        return

    for forest in summary["forests"]:
        _render_forest(forest, updated_state, today)
