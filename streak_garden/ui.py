"""Profile-only Streak Forest interface, backed by the existing durable engine."""
from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path

import streamlit as st

import learning_maintenance
import milestones as milestone_logic
import state
from . import engine
from .enums import GrowthStage
from .models import default_garden_state
from .rules import tree_sale_value

_ART_DIR = Path(__file__).resolve().parents[1] / "assets" / "streak_forest"
_STAGE_ASSETS = {
    GrowthStage.SEEDLING: "tree_seedling.svg",
    GrowthStage.SAPLING: "tree_sapling.svg",
    GrowthStage.MATURE: "tree_mature.svg",
}


def _asset_html(filename: str, alt: str, width: int = 72) -> str:
    """Embed a local, original SVG so the interface has no remote asset dependency."""
    path = _ART_DIR / filename
    try:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    except OSError:
        return f"<span role='img' aria-label='{alt}'>🌳</span>"
    return (
        f"<img src='data:image/svg+xml;base64,{encoded}' alt='{alt}' "
        f"width='{width}' height='{width}' style='object-fit:contain;display:block;margin:auto'/>"
    )


def _milestone_forest_id(milestone: dict) -> str:
    return f"milestone_{int(milestone['id'])}"


def _milestone_forest_map(milestones: list[dict]) -> dict[str, str]:
    return {
        _milestone_forest_id(item): str(item.get("title") or "Milestone")[:100]
        for item in milestones
        if isinstance(item, dict) and isinstance(item.get("id"), int)
    }


def _render_tree_collection(forest: dict, garden_state: dict, today) -> None:
    active_trees = list(forest["active_trees"])
    sold_trees = list(forest["sold_trees"])
    st.markdown("**Your trees**")
    if not active_trees and not sold_trees:
        st.caption("Complete enough learning days in this cycle to grow your first tree.")
    columns = st.columns(5)
    for index in range(int(forest["tree_capacity"])):
        with columns[index % 5]:
            if index < len(active_trees):
                tree = active_trees[index]
                stage = GrowthStage(int(tree["growth_stage"]))
                st.markdown(
                    _asset_html(_STAGE_ASSETS[stage], stage.name.title(), 62),
                    unsafe_allow_html=True,
                )
                st.caption(stage.name.title())
            else:
                st.markdown(
                    "<div style='height:72px;border:1px dashed var(--vc-border,#9ca3af);"
                    "border-radius:12px;background:var(--vc-surface-alt,rgba(128,128,128,.08));"
                    "display:flex;align-items:center;justify-content:center;color:var(--vc-muted,#8b929b)'>"
                    "Empty</div>",
                    unsafe_allow_html=True,
                )
    for tree in active_trees:
        stage = GrowthStage(int(tree["growth_stage"]))
        left, right = st.columns([3, 1.4], vertical_alignment="center")
        with left:
            st.write(f"{stage.name.title()} · planted {tree['planted_on']}")
        with right:
            value = tree_sale_value(tree["growth_stage"])
            if st.button(
                f"Sell · {value} Dew",
                key=f"streak_forest_sell_{tree['id']}",
                use_container_width=True,
            ):
                updated, paid = engine.sell_tree(garden_state, tree["id"], today)
                st.session_state.streak_garden = updated
                state.mark_persistent_dirty()
                st.toast(f"Tree sold · +{paid} Dew")
                st.rerun()
    if sold_trees:
        st.caption(
            f"{len(sold_trees)} sold tree(s) are retained in your milestone history."
        )


def _render_milestone_card(
    milestone: dict,
    forest: dict | None,
    garden_state: dict,
    today,
) -> None:
    title = str(milestone.get("title") or "Untitled milestone")
    emoji = str(milestone.get("emoji") or "🎯")
    with st.container(border=True):
        if forest is None:
            st.markdown(
                "<div style='height:96px;border:1px dashed var(--vc-border,#9ca3af);"
                "border-radius:14px;background:var(--vc-surface-alt,rgba(128,128,128,.09));"
                "display:flex;align-items:center;justify-content:center;color:var(--vc-muted,#8b929b);"
                "font-size:1.8rem'>＋</div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**{emoji} {title}**")
            st.caption("No forest attached to this milestone yet.")
            if st.button(
                "Add milestone forest",
                key=f"add_milestone_forest_{milestone['id']}",
                use_container_width=True,
            ):
                st.session_state.streak_garden_add_milestone_id = int(milestone["id"])
                st.rerun()
            return

        header, metric = st.columns([4, 1])
        with header:
            st.markdown(f"**{emoji} {title} Forest**")
            st.caption(
                f"{forest['qualifying_days']} / {forest['target_days']} learning days "
                f"· {forest['percentage']}% grassland"
            )
        with metric:
            st.metric("Trees", f"{forest['active_tree_count']}/{forest['tree_capacity']}")
        st.progress(int(forest["percentage"]))
        scene = _asset_html("forest_landscape.svg", "Illustrated green forest landscape", 260)
        st.markdown(
            "<div style='border-radius:14px;overflow:hidden;background:var(--vc-surface-alt,rgba(128,128,128,.08));padding:.35rem'>"
            + scene + "</div>",
            unsafe_allow_html=True,
        )
        if forest["is_full"]:
            st.caption("Forest full. Sell a tree to free one of its limited slots.")
        elif forest["current_cycle_tree_exists"]:
            st.caption("Milestone reached. Additional learning days grow your tree.")
        else:
            remaining = max(0, forest["target_days"] - forest["qualifying_days"])
            st.caption(
                f"{remaining} more learning {'day' if remaining == 1 else 'days'} "
                "to grow this cycle's tree."
            )
        with st.expander("Tree slots and rewards"):
            _render_tree_collection(forest, garden_state, today)


def render(progress: dict, profile: dict) -> None:
    """Keep the forest collapsed until requested; all UI remains inside Profile."""
    timezone_label = (
        profile.get("timezone", "Prefer not to say")
        if isinstance(profile, dict)
        else "Prefer not to say"
    )
    local_timezone = learning_maintenance.timezone_from_profile(timezone_label)
    today = datetime.now(local_timezone).date()
    active_by_course = learning_maintenance.activity_dates_by_course(
        progress, timezone_label
    )
    all_active_dates = learning_maintenance.activity_dates(progress, timezone_label)
    milestone_rows = milestone_logic.sanitize_milestones(
        st.session_state.get("milestones", [])
    )
    milestone_names = _milestone_forest_map(milestone_rows)
    active_for_each_milestone = {
        forest_id: set(all_active_dates) for forest_id in milestone_names
    }

    current_state = st.session_state.get("streak_garden", default_garden_state())
    # Legacy course forests are retained in storage for backwards compatibility.
    # New milestone forests are created only when the learner explicitly adds one.
    selected_id = st.session_state.get("streak_garden_add_milestone_id")
    if selected_id is not None:
        milestone = next((m for m in milestone_rows if m["id"] == selected_id), None)
        if milestone:
            forest_id = _milestone_forest_id(milestone)
            if forest_id not in current_state.get("forests", {}):
                updated, changed = engine.synchronize_garden(
                    current_state,
                    {forest_id: str(milestone.get("title") or "Milestone")},
                    {forest_id: set(all_active_dates)},
                    all_active_dates,
                    today,
                )
                current_state = updated
                if changed:
                    state.mark_persistent_dirty()
            st.session_state.pop("streak_garden_add_milestone_id", None)
            st.session_state.streak_garden = current_state

    # Reconcile only already-created milestone forests; don't create one per course.
    existing_names = {
        key: value for key, value in milestone_names.items()
        if key in current_state.get("forests", {})
    }
    if existing_names:
        current_state, changed = engine.synchronize_garden(
            current_state,
            existing_names,
            {key: set(all_active_dates) for key in existing_names},
            all_active_dates,
            today,
        )
        if changed:
            state.mark_persistent_dirty()
        st.session_state.streak_garden = current_state

    summary = engine.garden_summary(
        current_state,
        {key: set(all_active_dates) for key in existing_names},
        all_active_dates,
        today,
    )
    forest_lookup = {item["course_id"]: item for item in summary["forests"]}

    st.markdown("#### Learning Rhythm")
    st.caption(
        "Every completed lesson counts toward your learning streak, regardless of "
        "subject or course. A day is counted once even if you complete several lessons."
    )
    st.metric("Current streak", f"💧 {summary['current_streak']} days")
    st.metric("Dew", summary["dew_balance"])
    if not st.session_state.get("streak_forest_open", False):
        if st.button("View streak forest", key="view_streak_forest", type="primary"):
            st.session_state.streak_forest_open = True
            st.rerun()
        return

    if st.button("← Back to Profile", key="close_streak_forest"):
        st.session_state.streak_forest_open = False
        st.rerun()

    st.markdown("### Your Streak Forest")
    st.caption(
        "Each milestone can have one forest. Grey spaces are milestones without a "
        "forest yet. Complete lessons in any course to water every active milestone forest."
    )
    total_slots = len(milestone_rows)
    assigned = sum(
        1 for item in milestone_rows
        if _milestone_forest_id(item) in current_state.get("forests", {})
    )
    st.caption(f"{assigned} / {total_slots} milestone forests created")

    if not milestone_rows:
        st.info("Create a milestone in Profile's milestone tracker first. Its forest will appear here.")
        return

    cards = st.columns(2)
    for index, milestone in enumerate(milestone_rows):
        with cards[index % 2]:
            forest_id = _milestone_forest_id(milestone)
            _render_milestone_card(
                milestone,
                forest_lookup.get(forest_id),
                current_state,
                today,
            )
