import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from datetime import datetime

def send_reminder_email(sender_email, sender_password, receiver_email, tasks_df):
    """
    Sends an HTML email reminder summarizing overdue and upcoming tasks.
    """
    if tasks_df.empty:
        return False, "Không có công việc nào cần nhắc nhở."
        
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "⏰ [DMT Group] Nhắc nhở tiến độ công việc"
        msg["From"] = sender_email
        msg["To"] = receiver_email
        
        # Build HTML table for tasks
        tasks_html = ""
        for _, row in tasks_df.iterrows():
            status = str(row.get('TrangThai', ''))
            color = "#000"
            if "Trễ hạn" in status or "Quá hạn" in status:
                color = "red"
            elif "Vướng mắc" in status:
                color = "orange"
                
            tasks_html += f'''
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">{row.get('TenDuAn', '')}</td>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>{row.get('TenCongViec', '')}</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{row.get('Deadline', '')}</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: {color}; font-weight: bold;">{status}</td>
            </tr>
            '''
            
        html_content = f"""
        <html>
        <head>
            <style>
                table {{ border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; }}
                th {{ background-color: #f2f2f2; padding: 12px; text-align: left; border: 1px solid #ddd; }}
                td {{ padding: 8px; border: 1px solid #ddd; }}
            </style>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #1a73e8;">Xin chào! Dưới đây là danh sách công việc cần lưu ý:</h2>
            <p>Hệ thống ghi nhận bạn đang có một số công việc trễ hạn hoặc sắp đến hạn. Vui lòng kiểm tra và cập nhật tiến độ trên hệ thống.</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Dự án / Hạng mục</th>
                        <th>Tên công việc</th>
                        <th>Hạn chót</th>
                        <th>Trạng thái</th>
                    </tr>
                </thead>
                <tbody>
                    {tasks_html}
                </tbody>
            </table>
            
            <p style="margin-top: 20px; font-size: 12px; color: #777;">
                <i>Đây là email tự động từ Hệ thống Quản lý Tiến độ DMT Group. Vui lòng không trả lời email này.</i>
            </p>
        </body>
        </html>
        """
        
        part = MIMEText(html_content, "html")
        msg.attach(part)
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        
        return True, "Gửi email thành công!"
    except Exception as e:
        return False, f"Lỗi khi gửi mail: {str(e)}"
