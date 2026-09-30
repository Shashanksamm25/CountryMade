import streamlit as st

from db import execute, fetch_all
from utils import money, show_image


def _cloth_grid(category: str, user_id: int):
    rows = fetch_all(
        "SELECT * FROM clothes WHERE category = %s ORDER BY id DESC", (category,)
    )
    if not rows:
        st.info("No clothes found.")
        return

    search = st.text_input("🔍 Search by name or brand", key=f"search_{category}")
    if search:
        s = search.lower()
        rows = [r for r in rows
                if s in (r["name"] or "").lower() or s in (r["brand"] or "").lower()]

    for start in range(0, len(rows), 3):
        cols = st.columns(3)
        for col, item in zip(cols, rows[start:start + 3]):
            with col, st.container(border=True):
                show_image(item["image_path"], use_container_width=True)
                st.markdown(f"**{item['name']}**")
                if item["brand"]:
                    st.caption(f"Brand: {item['brand']}")
                if item["size"]:
                    st.caption(f"Size: {item['size']}")
                if item["info"]:
                    st.write(item["info"])
                st.markdown(f"<span class='price'>{money(item['price'])}</span>",
                            unsafe_allow_html=True)
                if st.button("🤍 Add to Wishlist", key=f"wl_{item['id']}"):
                    row = execute(
                        "INSERT INTO wishlist (user_id, cloth_id) VALUES (%s, %s) "
                        "ON CONFLICT (user_id, cloth_id) DO NOTHING RETURNING id",
                        (user_id, item["id"]),
                        returning=True,
                    )
                    if row:
                        st.toast("Added to wishlist", icon="✅")
                    else:
                        st.toast("Already in wishlist", icon="ℹ️")


def render_mens(auth):
    st.markdown(
        "<h1>👔 Men's <span style='color:#C67B5C'>Wear</span></h1>",
        unsafe_allow_html=True,
    )
    _cloth_grid("men", auth["id"])


def render_womens(auth):
    st.markdown(
        "<h1>👗 Women's <span style='color:#C67B5C'>Wear</span></h1>",
        unsafe_allow_html=True,
    )
    _cloth_grid("women", auth["id"])


def render_wishlist(auth):
    st.markdown(
        "<h1>💜 Your <span style='color:#C67B5C'>Wishlist</span></h1>",
        unsafe_allow_html=True,
    )
    rows = fetch_all(
        """
        SELECT c.*, w.id AS wishlist_id
        FROM wishlist w
        JOIN clothes c ON c.id = w.cloth_id
        WHERE w.user_id = %s
        ORDER BY w.added_on DESC
        """,
        (auth["id"],),
    )
    if not rows:
        st.info("No items in your wishlist.")
        return

    for item in rows:
        with st.container(border=True):
            c_img, c_info, c_btn = st.columns([1, 3, 1])
            with c_img:
                show_image(item["image_path"], use_container_width=True)
            with c_info:
                st.markdown(f"**{item['name']}**  ·  _{item['category'].title()}_")
                st.caption(f"Brand: {item['brand'] or '—'}  |  Size: {item['size'] or '—'}")
                if item["info"]:
                    st.write(item["info"])
                st.markdown(f"<span class='price'>{money(item['price'])}</span>",
                            unsafe_allow_html=True)
            with c_btn:
                if st.button("Remove", key=f"rm_{item['wishlist_id']}", type="primary"):
                    execute(
                        "DELETE FROM wishlist WHERE id = %s AND user_id = %s",
                        (item["wishlist_id"], auth["id"]),
                    )
                    st.toast("Removed from wishlist")
                    st.rerun()
