import base64
from io import BytesIO
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image as PILImage

from auth import login_admin, login_user, register_user
from db import execute

SLIDES_DIR = Path("assets/slides")

REVIEWS = [
    ("Kushal N", "Kushal .jpg"),
    ("Shashank R", "Shashank R.jpg"),
    ("Salaar", "mypic2.jpg"),
    ("Kalki", "me2.jpg"),
    ("Rakesh R", "Raki.jpg"),
    ("Shashank BV", "bv.png"),
    ("Ranganath P", "ranga.png"),
    ("Somashekar", "soma.png"),
]
LOREM = ("Lorem ipsum dolor sit amet consectetur, adipisicing elit. "
         "Ipsam incidunt quod praesentium iusto id autem possimus assumenda at ut saepe.")


def _slideshow():
    slides = sorted(
        p for p in SLIDES_DIR.glob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    ) if SLIDES_DIR.exists() else []
    if not slides:
        st.info("Add images to `assets/slides/` to show the slideshow.")
        return

    # Build base64 encoded images for an HTML-based auto-slideshow
    images_html = ""
    dots_html = ""
    for i, slide_path in enumerate(slides):
        data = slide_path.read_bytes()
        ext = slide_path.suffix.lower().replace(".", "")
        mime = f"image/{'jpeg' if ext in ('jpg', 'jpeg') else 'png'}"
        b64 = base64.b64encode(data).decode()
        active = "active" if i == 0 else ""
        images_html += (
            f'<div class="slide-item {active}" id="slide-{i}">'
            f'<img src="data:{mime};base64,{b64}" alt="Slide {i+1}">'
            f'</div>'
        )
        dots_html += f'<span class="dot {active}" onclick="goToSlide({i})"></span>'

    html = f"""
    <style>
        .slide-container {{ position: relative; width: 100%; height: 440px; overflow: hidden; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);}}
        .slide-item {{ position: absolute; width: 100%; height: 100%; opacity: 0; transition: opacity 0.8s ease-in-out;}}
        .slide-item.active {{ opacity: 1;}}
        .slide-item img {{ width: 100%; height: 100%; object-fit: cover;}}
        .slide-dots {{ text-align: center; padding: 12px 0;}}
        .slide-dots .dot {{
            height: 11px; width: 11px; margin: 0 5px;
            background: #D2B48C; border-radius: 50%;
            display: inline-block; cursor: pointer;
            transition: all .3s ease;
        }}
        .slide-dots .dot.active {{
            background: #C67B5C; transform: scale(1.35);
            box-shadow: 0 0 6px rgba(198,123,92,0.5);
        }}
    </style>
    <div class="slide-container">
        {images_html}
    </div>
    <div class="slide-dots">{dots_html}</div>
    <script>
        let currentSlide = 0;
        const totalSlides = {len(slides)};
        function showSlide(n) {{
            const slides = document.querySelectorAll('.slide-item');
            const dots = document.querySelectorAll('.dot');
            slides.forEach(s => s.classList.remove('active'));
            dots.forEach(d => d.classList.remove('active'));
            currentSlide = ((n % totalSlides) + totalSlides) % totalSlides;
            slides[currentSlide].classList.add('active');
            dots[currentSlide].classList.add('active');
        }}
        function goToSlide(n) {{ showSlide(n); }}
        setInterval(() => showSlide(currentSlide + 1), 4000);
    </script>
    """
    if hasattr(st, "iframe"):  # newer Streamlit (components.html is being removed)
        st.iframe(html, height=490)
    else:
        components.html(html, height=490, scrolling=False)


def _stats():
    c1, c2, c3 = st.columns(3)
    for col, num, label, icon in [
        (c1, "150+", "Branches", "🏬"),
        (c2, "477000+", "Products", "👖"),
        (c3, "320+", "Happy Customers", "😊"),
    ]:
        col.markdown(
            f"<div class='stat'>"
            f"<div style='font-size:1.8rem; margin-bottom:.3rem;'>{icon}</div>"
            f"<h3>{num}</h3><p>{label}</p></div>",
            unsafe_allow_html=True,
        )


def _reviews():
    st.markdown("## Client's <span>Review</span>", unsafe_allow_html=True)
    for start in range(0, len(REVIEWS), 4):
        cols = st.columns(4)
        for col, (name, img) in zip(cols, REVIEWS[start:start + 4]):
            with col:
                # Build base64 circular avatar
                img_html = ""
                path = Path("assets/reviewers") / img
                if path.exists():
                    pil_img = PILImage.open(path).convert("RGB")
                    src_w, src_h = pil_img.size
                    tgt = 200
                    scale = max(tgt / src_w, tgt / src_h)
                    new_w, new_h = int(src_w * scale), int(src_h * scale)
                    pil_img = pil_img.resize((new_w, new_h), PILImage.Resampling.LANCZOS)
                    left = (new_w - tgt) // 2
                    top_c = (new_h - tgt) // 2
                    pil_img = pil_img.crop((left, top_c, left + tgt, top_c + tgt))
                    buf = BytesIO()
                    pil_img.save(buf, format="JPEG", quality=85)
                    b64 = base64.b64encode(buf.getvalue()).decode()
                    img_html = (
                        f"<img src='data:image/jpeg;base64,{b64}' "
                        f"style='width:100px;height:100px;border-radius:50%;object-fit:cover;"
                        f"border:3px solid #E8A87C;margin-bottom:.6rem;'>"
                    )
                st.markdown(
                    f"<div style='background:linear-gradient(135deg,#fff,#FDF6F0);"
                    f"border-radius:1rem;padding:1.2rem;text-align:center;"
                    f"box-shadow:0 4px 20px rgba(92,64,51,0.08);"
                    f"border:1px solid rgba(198,123,92,0.15);"
                    f"min-height:320px;display:flex;flex-direction:column;"
                    f"align-items:center;justify-content:center;"
                    f"transition:transform .3s ease;'>"
                    f"{img_html}"
                    f"<p style='font-size:.82rem;color:#6B4F3A;margin:.3rem 0;'>{LOREM}</p>"
                    f"<h4 style='color:#5C4033;margin:.4rem 0 .2rem;'>{name}</h4>"
                    f"<div style='color:#E8A87C;font-size:1.2rem;'>★★★★½</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )


def _contact():
    st.markdown("## <span>Contact</span> Us", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.map({"lat": [19.1417], "lon": [72.8232]}, zoom=11)  # Jogeshwari West, Mumbai
    with right, st.form("contact_form", clear_on_submit=True):
        st.subheader("Get in touch")
        name = st.text_input("Your name")
        email = st.text_input("Your email")
        subject = st.text_input("Subject")
        message = st.text_area("Your message", height=150)
        if st.form_submit_button("Send message"):
            if name and email and message:
                execute(
                    "INSERT INTO contact_messages (name, email, subject, message) "
                    "VALUES (%s, %s, %s, %s)",
                    (name.strip(), email.strip(), subject.strip(), message.strip()),
                )
                st.success("Thanks! Your message has been sent.")
            else:
                st.warning("Name, email and message are required.")


def _footer():
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.markdown("**Quick Links**\n\n➜ Home\n\n➜ Men's\n\n➜ Women's\n\n➜ Reviews\n\n➜ Contact")
    c2.markdown("**Contact Info**\n\n📞 +919900113395\n\n📞 +9900113394\n\n"
                "✉️ SAMZJEANS@NAMMA.com\n\n📍 KARNATAKA - INDIA - 570016")
    c3.markdown("**Follow Us**\n\nFacebook\n\nTwitter\n\nInstagram\n\nLinkedIn\n\nPinterest")
    st.markdown(
        "<div style='text-align:center; padding:1rem 0; color:#6B4F3A; font-size:.85rem;'>"
        "© 2015 Country Made · All Rights Reserved</div>",
        unsafe_allow_html=True,
    )


def render_home(auth=None):
    if auth:
        st.markdown(
            f"""
            <style>
            @keyframes welcomeSlideIn {{
                0% {{ opacity: 0; transform: translateY(-20px) scale(0.97); }}
                100% {{ opacity: 1; transform: translateY(0) scale(1); }}
            }}
            @keyframes shimmer {{
                0% {{ background-position: -200% center; }}
                100% {{ background-position: 200% center; }}
            }}
            @keyframes wave {{
                0%,100% {{ transform: rotate(0deg); }}
                20% {{ transform: rotate(14deg); }}
                40% {{ transform: rotate(-8deg); }}
                60% {{ transform: rotate(14deg); }}
                80% {{ transform: rotate(-4deg); }}
            }}
            @keyframes glowPulse {{
                0%,100% {{ box-shadow: 0 4px 20px rgba(198,123,92,0.25); }}
                50% {{ box-shadow: 0 6px 35px rgba(198,123,92,0.45); }}
            }}
            .welcome-anim {{
                background: linear-gradient(135deg, #5C4033, #C67B5C, #E8A87C, #C67B5C);
                background-size: 200% auto;
                animation: welcomeSlideIn 0.7s ease-out, shimmer 4s ease infinite, glowPulse 3s ease-in-out infinite;
                border-radius: 1.2rem;
                padding: 1.5rem 2rem;
                margin-bottom: 1.2rem;
                border: 1px solid rgba(232,168,124,0.3);
            }}
            .welcome-anim .wa-wave {{
                display: inline-block;
                font-size: 1.8rem;
                animation: wave 1.8s ease-in-out infinite;
                transform-origin: 70% 70%;
                margin-right: .4rem;
            }}
            .welcome-anim .wa-greeting {{
                font-size: 1.5rem;
                font-weight: 700;
                color: #FDF6F0;
                letter-spacing: .5px;
                display: block;
                margin-bottom: .3rem;
            }}
            .welcome-anim .wa-name {{
                color: #FFE0C2;
                text-shadow: 0 1px 6px rgba(0,0,0,0.15);
            }}
            .welcome-anim .wa-sub {{
                font-size: .95rem;
                color: rgba(253,246,240,0.85);
                font-weight: 400;
                letter-spacing: .3px;
            }}
            </style>
            <div class="welcome-anim">
                <span class="wa-greeting">
                    <span class="wa-wave">👋</span>
                    Welcome back, <span class="wa-name">{auth['username']}</span>!
                </span>
                <span class="wa-sub">Explore our latest denim collection — curated just for you ✦</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='hero'>Find Your Fashion</div>", unsafe_allow_html=True)
    _slideshow()
    st.write("")
    _stats()
    st.write("")
    _reviews()
    st.write("")
    _contact()
    _footer()


def render_user_login():
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown(
            "<div style='text-align:center; margin-bottom:1rem;'>"
            "<span style='font-size:3rem;'>🔑</span>"
            "<h2 style='margin:.5rem 0 0;'>Welcome Back</h2>"
            "<p style='color:#6B4F3A;'>Sign in to your account</p></div>",
            unsafe_allow_html=True,
        )
        with st.form("user_login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                if login_user(username, password):
                    st.session_state["page"] = "Home"
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        if st.button("Don't have an account? Sign up"):
            st.session_state["page"] = "Register"
            st.rerun()


def render_register():
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown(
            "<div style='text-align:center; margin-bottom:1rem;'>"
            "<span style='font-size:3rem;'>📝</span>"
            "<h2 style='margin:.5rem 0 0;'>Create Account</h2>"
            "<p style='color:#6B4F3A;'>Join our community</p></div>",
            unsafe_allow_html=True,
        )
        with st.form("register"):
            username = st.text_input("Username")
            email = st.text_input("E-mail")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Register", use_container_width=True):
                ok, msg = register_user(username, email, password)
                (st.success if ok else st.error)(msg)
        if st.button("Back to login"):
            st.session_state["page"] = "User Login"
            st.rerun()


def render_admin_login():
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown(
            "<div style='text-align:center; margin-bottom:1rem;'>"
            "<span style='font-size:3rem;'>🛡️</span>"
            "<h2 style='margin:.5rem 0 0;'>Admin Portal</h2>"
            "<p style='color:#6B4F3A;'>Authorized personnel only</p></div>",
            unsafe_allow_html=True,
        )
        with st.form("admin_login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                if login_admin(username, password):
                    st.session_state["page"] = "Dashboard"
                    st.rerun()
                else:
                    st.error("Username/password is incorrect.")