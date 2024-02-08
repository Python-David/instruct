import smtplib

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 465  # Use SSL port

def test_smtp_connection(host, port):
    try:
        with smtplib.SMTP_SSL(host, port) as smtp:
            print(f"Successfully connected to {host} on port {port}.")
    except Exception as e:
        print(f"Failed to connect to {host} on port {port}. Error: {e}")

test_smtp_connection(SMTP_HOST, SMTP_PORT)
