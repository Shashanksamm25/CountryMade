import streamlit as st

import views_admin as admin
import views_public as public
import views_user as user
from auth import current_auth, logout
from utils import inject_css

st.set_page_config(page_title="Country Made", page_icon="👖", layout="wide")
inject_css()

GUEST_PAGES = {
    "🏠 Home": "Home",
    "🔑 User Login": "User Login",
    "📝 Register": "Register",
    "🛡️ Admin Login": "Admin Login",
}
USER_PAGES = {
    "🏠 Home": "Home",
    "👔 Men's": "Men's",
    "👗 Women's": "Women's",
    "💜 My Wishlist": "My Wishlist",
}
ADMIN_PAGES = {
    "📊 Dashboard": "Dashboard",
    "👔 Add Men's": "Add Men's",
    "👗 Add Women's": "Add Women's",
    "🗂️ Manage Clothes": "Manage Clothes",
}

auth = current_auth()
page_map = ADMIN_PAGES if auth and auth["role"] == "admin" else \
           USER_PAGES if auth else GUEST_PAGES

labels = list(page_map.keys())
values = list(page_map.values())
st.session_state.setdefault("page", values[0])
if st.session_state["page"] not in values:
    st.session_state["page"] = values[0]
current_idx = (values.index(st.session_state["page"]) if
               st.session_state["page"] in values else 0)

with st.sidebar:
    st.markdown("<div class='brand'><span>Country</span>Made</div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color:#D2B48C; font-size:.85rem; "
        "margin: -.5rem 0 1rem; letter-spacing: 1px;'>✦ Premium Denim Since 2015 ✦</p>",
        unsafe_allow_html=True,
    )
    selected_label = st.radio(
        "Navigate", labels, index=current_idx,
        label_visibility="collapsed",
    )
    st.session_state["page"] = page_map[selected_label]
    st.divider()
    if auth:
        role_icon = "🛡️" if auth["role"] == "admin" else "👤"
        st.markdown(
            f"<div style='text-align:center; padding:.5rem; background:rgba(198,123,92,0.15); "
            f"border-radius:.6rem; margin-bottom:.5rem;'>"
            f"<div style='font-size:1.4rem;'>{role_icon}</div>"
            f"<div style='font-weight:600; font-size:.95rem;'>{auth['username']}</div>"
            f"<div style='font-size:.75rem; color:#D2B48C;'>{auth['role'].upper()}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    else:
        st.markdown(
            "<div style='text-align:center; padding:.5rem; opacity:.7; font-size:.85rem;'>"
            "Sign in to access your wishlist and more</div>",
            unsafe_allow_html=True,
        )

page = st.session_state["page"]

if not auth:
    {
        "Home": lambda: public.render_home(),
        "User Login": public.render_user_login,
        "Register": public.render_register,
        "Admin Login": public.render_admin_login,
    }[page]()
elif auth["role"] == "user":
    {
        "Home": lambda: public.render_home(auth),
        "Men's": lambda: user.render_mens(auth),
        "Women's": lambda: user.render_womens(auth),
        "My Wishlist": lambda: user.render_wishlist(auth),
    }[page]()
else:
    {
        "Dashboard": lambda: admin.render_dashboard(auth),
        "Add Men's": lambda: admin.render_add_mens(auth),
        "Add Women's": lambda: admin.render_add_womens(auth),
        "Manage Clothes": lambda: admin.render_manage(auth),
    }[page]()
