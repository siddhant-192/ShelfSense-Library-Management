from celery import shared_task
from models import *
from .mail_service import send_message
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, date, timedelta
from sqlalchemy import func
import calendar

@shared_task(ignore_result=True)
def daily_reminder(subject):

    utc_now = datetime.utcnow()
    today = utc_now.date()

    # Get users who haven't logged in today
    users = User.query.filter(
        User.last_login_at != None,
        func.date(User.last_login_at) != today
    ).all()

    # Load the HTML template
    env = Environment(loader=FileSystemLoader('/Users/phoenix/Desktop/ShelfSense/celery_files'))
    template = env.get_template('reminder_template.html')

    for user in users:
        # Render the template with user-specific data
        email_body = template.render(username=user.username)

        # Modify the subject to include the user's username
        email_subject = f"{user.username}, {subject}"

        # Send the email
        send_message(user.email, email_subject, email_body)

    return "Reminder sent successfully."



@shared_task(ignore_result=True)
def monthly_report():
    # Get the last month
    utc_now = datetime.utcnow()
    today = utc_now.date()
    last_month = (today - timedelta(days=28)).month # Get the previous month

    users = User.query.all()

    for user in users:
        # Query the database for the required data for the current user
        user_id = user.id

        # Get the count of books issued this month
        books_issued = bookissue.query.filter(
            bookissue.user_id == user_id,
            func.extract('month', bookissue.date_issued) == last_month
        ).count()

        # Get the count of books returned this month (including those not issued this month)
        books_returned = bookissue.query.filter(
            bookissue.user_id == user_id,
            bookissue.return_date.between(
                datetime(today.year, last_month, 1),
                datetime(today.year, last_month, calendar.monthrange(today.year, last_month)[1])
            )
        ).count()

        # Get the list of books issued this month
        issued_books = bookissue.query.filter(
            bookissue.user_id == user_id,
            func.extract('month', bookissue.date_issued) == last_month
        ).all()

        # Retrieve book names for issued books
        issued_books_with_names = []
        for issue in issued_books:
            book_id = issue.book_id
            book = Book.query.filter_by(id=book_id).first()
            if book:
                issued_books_with_names.append((book_id, book.name))


        # Get the list of books returned this month
        returned_books = bookissue.query.filter(
            bookissue.user_id == user_id,
            func.extract('month', bookissue.return_date) == last_month
        ).all()

        # Retrieve book names for returned books
        returned_books_with_names = []
        for issue in returned_books:
            book_id = issue.book_id
            book = Book.query.filter_by(id=book_id).first()
            if book:
                returned_books_with_names.append((book_id, book.name))

        # Get the list of currently issued books for the current month
        currently_issued_books = bookissue.query.filter(
            bookissue.user_id == user_id,
            bookissue.return_date == None,
            func.extract('month', bookissue.date_issued) == last_month
        ).all()

        # Retrieve book names for currently issued books
        currently_issued_books_with_names = []
        for issue in currently_issued_books:
            book_id = issue.book_id
            book = Book.query.filter_by(id=book_id).first()
            if book:
                currently_issued_books_with_names.append((book_id, book.name))

        # Get the section IDs of the issued books for the current month
        issued_section_ids = db.session.query(Book.section_id).join(bookissue).filter(
            bookissue.user_id == user_id
        ).distinct().all()

        # Extract section IDs from the query result
        issued_section_ids = [section_id for section_id, in issued_section_ids]

        # Query sections explored based on the section IDs from issued books this month
        sections_explored = Section.query.join(Book).filter(
            Book.section_id.in_(issued_section_ids)
        ).distinct().all()

        # Load the HTML template
        env = Environment(loader=FileSystemLoader('/Users/phoenix/Desktop/ShelfSense/celery_files'))
        template = env.get_template('monthly_template.html')

        # Render the template with user-specific data
        email_body = template.render(
            username=user.username,
            books_issued=books_issued,
            books_returned=books_returned,
            books_issued_list=issued_books_with_names,
            books_returned_list=returned_books_with_names,
            currently_issued_books=currently_issued_books_with_names,
            sections_explored=sections_explored
        )

        # Modify the subject to include the user's username
        email_subject = f"{user.username}, Monthly Report"

        # Send the email
        send_message(user.email, email_subject, email_body)

    return "Monthly reports sent successfully."
    # Get the last month
    #last_month = (date.today() - timedelta(days=28)).month
    utc_now = datetime.utcnow()
    today = utc_now.date()
    last_month = (today).month

    users = User.query.all()

    for user in users:
        # Query the database for the required data for the current user
        user_id = user.id
        
        books_read1 = bookissue.query.filter(
            bookissue.user_id == user_id,
            func.extract('month', bookissue.return_date) == last_month
        ).count()

        books_read2 = bookissue.query.filter(
            bookissue.user_id == user_id,
            func.extract('month', bookissue.date_issued) == last_month
        ).count()

        books_read = books_read1 + books_read2
        
        books_issued = bookissue.query.filter(
            bookissue.user_id == user_id
        ).all()
        
        books_returned = bookissue.query.filter(
            bookissue.user_id == user_id
        ).all()
        
        currently_issued_books = bookissue.query.filter(
            bookissue.user_id == user_id,
            bookissue.return_date == None
        ).all()
        
        # Get the section IDs of the issued books for the current month
        issued_section_ids = db.session.query(Book.section_id).join(bookissue).filter(
            bookissue.user_id == user_idl
        ).distinct().all()

        # Extract section IDs from the query result
        issued_section_ids = [section_id for section_id, in issued_section_ids]

        # Query sections explored based on the section IDs from issued books this month
        sections_explored = Section.query.join(Book).filter(
            Book.section_id.in_(issued_section_ids)
        ).distinct().all()


        # Load the HTML template
        env = Environment(loader=FileSystemLoader('/Users/phoenix/Desktop/ShelfSense/celery_files'))  # Update the path to your templates directory
        template = env.get_template('monthly_template.html')  # Update the template name as needed

        # Render the template with user-specific data
        email_body = template.render(
            username=user.username,
            books_read=books_read,
            books_issued=books_issued,
            books_returned=books_returned,
            currently_issued_books=currently_issued_books,
            sections_explored=sections_explored
        )

        # Modify the subject to include the user's username
        email_subject = f"{user.username}, Monthly Report"

        # Send the email
        send_message(user.email, email_subject, email_body)

    return "Monthly reports sent successfully."