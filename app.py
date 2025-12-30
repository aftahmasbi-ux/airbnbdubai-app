import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- تنظیمات اولیه فایل ذخیره‌سازی ---
FILE_PATH = 'airbnb_data.csv'

# اگر فایل وجود نداشت، آن را با ستون‌های لازم بساز
if not os.path.exists(FILE_PATH):
    df_empty = pd.DataFrame(columns=[
        'Date_Entry', 'User', 'Apartment', 'Guest_Name', 
        'Check_In', 'Nights', 'Income_Net', 
        'Cost_Cleaning', 'Cost_Tourism', 'Cost_Other', 'Net_Profit'
    ])
    df_empty.to_csv(FILE_PATH, index=False)

# --- سیستم احراز هویت (ساده) ---
# در نسخه واقعی، این بخش باید به دیتابیس امن متصل شود
USERS = {
    "admin": "admin123",  # نام کاربری: admin, رمز: admin123
    "employee1": "emp123",
    "partner": "partner123"
}

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["username"] in USERS and st.session_state["password"] == USERS[st.session_state["username"]]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # پاک کردن پسورد از حافظه برای امنیت
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # نمایش فرم لاگین
        st.text_input("Username / نام کاربری", key="username")
        st.text_input("Password / رمز عبور", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # اگر رمز اشتباه بود
        st.text_input("Username / نام کاربری", key="username")
        st.text_input("Password / رمز عبور", type="password", on_change=password_entered, key="password")
        st.error("😕 نام کاربری یا رمز عبور اشتباه است.")
        return False
    else:
        # اگر رمز درست بود
        return True

# --- بدنه اصلی برنامه ---
if check_password():
    current_user = st.session_state["username"]
    
    # منوی کناری
    st.sidebar.title(f"خوش آمدید، {current_user} 👋")
    menu = st.sidebar.radio("منو", ["ثبت اطلاعات جدید", "داشبورد و گزارش‌ها", "جدول داده‌ها"])
    
    # بارگذاری داده‌ها
    df = pd.read_csv(FILE_PATH)

    # --- صفحه 1: ثبت اطلاعات ---
    if menu == "ثبت اطلاعات جدید":
        st.header("📝 ثبت رزرو جدید")
        
        with st.form("entry_form"):
            col1, col2 = st.columns(2)
            with col1:
                apt = st.selectbox("انتخاب آپارتمان", ["Apt 1 - Downtown", "Apt 2 - Marina", "Apt 3 - Future"])
                guest = st.text_input("نام میهمان")
                check_in = st.date_input("تاریخ ورود")
            with col2:
                nights = st.number_input("تعداد شب", min_value=1, step=1)
                income = st.number_input("دریافتی خالص (درآمد)", min_value=0.0)
            
            st.markdown("---")
            st.subheader("هزینه‌های متغیر این رزرو")
            col3, col4, col5 = st.columns(3)
            with col3:
                clean_cost = st.number_input("هزینه نظافت", min_value=0.0)
            with col4:
                tourist_cost = st.number_input("هزینه توریست دبی", min_value=0.0)
            with col5:
                other_cost = st.number_input("سایر هزینه‌ها", min_value=0.0)
                
            submitted = st.form_submit_button("ثبت در سیستم")
            
            if submitted:
                # محاسبه سود
                net_profit = income - clean_cost - tourist_cost - other_cost
                
                # ساخت رکورد جدید
                new_data = {
                    'Date_Entry': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'User': current_user,  # ذخیره نام کاربری که دیتا را وارد کرده
                    'Apartment': apt,
                    'Guest_Name': guest,
                    'Check_In': check_in,
                    'Nights': nights,
                    'Income_Net': income,
                    'Cost_Cleaning': clean_cost,
                    'Cost_Tourism': tourist_cost,
                    'Cost_Other': other_cost,
                    'Net_Profit': net_profit
                }
                
                # اضافه کردن به دیتافریم و ذخیره
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                df.to_csv(FILE_PATH, index=False)
                st.success(f"✅ اطلاعات با موفقیت توسط {current_user} ثبت شد!")

    # --- صفحه 2: داشبورد ---
    elif menu == "داشبورد و گزارش‌ها":
        st.header("📊 داشبورد مدیریتی")
        
        if not df.empty:
            # کارت‌های آماری بالای صفحه
            total_income = df['Income_Net'].sum()
            total_profit = df['Net_Profit'].sum()
            total_nights = df['Nights'].sum()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("درآمد کل", f"{total_income:,.0f}")
            c2.metric("سود خالص کل", f"{total_profit:,.0f}")
            c3.metric("تعداد شب‌های رزرو", f"{total_nights}")
            
            st.markdown("---")
            
            # نمودار سود بر اساس آپارتمان
            st.subheader("سودآوری به تفکیک آپارتمان")
            st.bar_chart(df.groupby("Apartment")["Net_Profit"].sum())
            
            # نمودار عملکرد ماهانه (ساده شده)
            st.subheader("روند درآمد بر اساس هر رزرو")
            st.line_chart(df['Income_Net'])
            
        else:
            st.info("هنوز داده‌ای ثبت نشده است.")

    # --- صفحه 3: نمایش جدول ---
    elif menu == "جدول داده‌ها":
        st.header("📋 لیست تمام تراکنش‌ها")
        st.write("در ستون User می‌توانید ببینید چه کسی اطلاعات را وارد کرده است.")
        st.dataframe(df)
        
        # دکمه دانلود خروجی اکسل
        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')

        csv = convert_df(df)
        st.download_button(
            label="دانلود فایل CSV",
            data=csv,
            file_name='airbnb_data.csv',
            mime='text/csv',
        )
