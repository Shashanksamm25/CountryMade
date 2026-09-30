import streamlit as st

from db import execute, fetch_all, fetch_one
from utils import SIZES, delete_image, money, save_image, show_image


def render_dashboard(auth):
    st.markdown(
        f"<h1 style='margin-bottom:.2rem;'>📊 Admin Dashboard</h1>"
        f"<p style='color:#6B4F3A; font-size:1rem; margin-bottom:1.5rem;'>"
        f"Signed in as <strong>{auth['username']}</strong></p>",
        unsafe_allow_html=True,
    )
    counts = fetch_one(
        """
        SELECT
          (SELECT COUNT(*) FROM clothes WHERE category='men')   AS men,
          (SELECT COUNT(*) FROM clothes WHERE category='women') AS women,
          (SELECT COUNT(*) FROM users)                          AS users,
          (SELECT COUNT(*) FROM contact_messages)               AS messages
        """
    )
    c1, c2, c3, c4 = st.columns(4)
    for col, val, label, icon in [
        (c1, counts["men"], "Men's Items", "👔"),
        (c2, counts["women"], "Women's Items", "👗"),
        (c3, counts["users"], "Registered Users", "👥"),
        (c4, counts["messages"], "Messages", "✉️"),
    ]:
        col.markdown(
            f"<div class='stat'>"
            f"<div style='font-size:1.5rem;'>{icon}</div>"
            f"<h3>{val}</h3><p>{label}</p></div>",
            unsafe_allow_html=True,
        )

    st.write("")
    with st.expander("📬 Contact messages"):
        msgs = fetch_all(
            "SELECT name, email, subject, message, created_at "
            "FROM contact_messages ORDER BY created_at DESC LIMIT 50"
        )
        if msgs:
            st.dataframe(msgs, use_container_width=True)
        else:
            st.caption("No messages yet.")


def _add_form(category: str):
    label = "Men's" if category == "men" else "Women's"
    icon = "👔" if category == "men" else "👗"
    st.markdown(
        f"<h1 style='margin-bottom:.2rem;'>{icon} Add {label} Cloth</h1>"
        f"<p style='color:#6B4F3A; margin-bottom:1rem;'>Fill in the details below</p>",
        unsafe_allow_html=True,
    )

    with st.form(f"add_{category}", clear_on_submit=True):
        name = st.text_input("Cloth name")
        image = st.file_uploader("Image", type=["jpg", "jpeg", "png"])
        col_a, col_b = st.columns(2)
        with col_a:
            brand = st.text_input("Brand")
            size = st.selectbox("Size", SIZES)
        with col_b:
            price = st.number_input("Price (₹)", min_value=0.0, step=1.0, format="%.2f")
        info = st.text_area("Additional information")
        submitted = st.form_submit_button("Add Cloth", use_container_width=True)

    if submitted:
        if not name.strip() or image is None:
            st.error("Name and image are required.")
            return
        try:
            filename = save_image(image)
        except ValueError as e:
            st.error(str(e))
            return
        execute(
            "INSERT INTO clothes (category, name, brand, size, info, price, image_path) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (category, name.strip(), brand.strip() or None, size, info.strip() or None,
             price, filename),
        )
        # ── Success card instead of balloons ──
        st.markdown(
            f"<div class='success-card'>"
            f"<span class='sc-icon'>✅</span>"
            f"<div class='sc-title'>Cloth Added Successfully!</div>"
            f"<div class='sc-sub'><strong>{name.strip()}</strong> has been added to {label} collection · "
            f"Brand: {brand.strip() or '—'} · Size: {size} · {money(price)}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )



def render_add_mens(auth):
    _add_form("men")


def render_add_womens(auth):
    _add_form("women")


def render_manage(auth):
    st.markdown(
        "<h1 style='margin-bottom:.5rem;'>🗂️ Manage Clothes</h1>",
        unsafe_allow_html=True,
    )
    category = st.radio("Category", ["men", "women"], horizontal=True,
                        format_func=lambda c: f"{'👔' if c == 'men' else '👗'} {c.title()}")
    rows = fetch_all(
        "SELECT * FROM clothes WHERE category = %s ORDER BY id DESC", (category,)
    )
    if not rows:
        st.info("Nothing here yet.")
        return
    for item in rows:
        with st.container(border=True):
            c_img, c_info, c_btn = st.columns([1, 4, 1])
            with c_img:
                show_image(item["image_path"], width=100)
            with c_info:
                st.markdown(f"**{item['name']}**  (#{item['id']})")
                st.caption(f"{item['brand'] or '—'} | Size {item['size'] or '—'} | "
                           f"{money(item['price'])}")
                if item["info"]:
                    st.write(item["info"])
            with c_btn:
                if st.button("Delete", key=f"del_{item['id']}", type="primary"):
                    execute("DELETE FROM clothes WHERE id = %s", (item["id"],))
                    delete_image(item["image_path"])
                    st.toast("Deleted")
                    st.rerun()
