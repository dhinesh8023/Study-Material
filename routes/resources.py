import os

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from extensions import db
from models import Resource

resources_bp = Blueprint("resources", __name__)

SUBJECTS = [
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "Computer Science",
    "Engineering",
    "Business",
    "Literature",
    "History",
    "Other",
]


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


@resources_bp.route("/")
def index():
    return redirect(url_for("resources.browse"))


@resources_bp.route("/browse")
def browse():
    query = request.args.get("q", "").strip()
    subject = request.args.get("subject", "").strip()

    resources_query = Resource.query

    if subject:
        resources_query = resources_query.filter(Resource.subject == subject)
    if query:
        like = f"%{query}%"
        resources_query = resources_query.filter(
            or_(
                Resource.title.ilike(like),
                Resource.description.ilike(like),
                Resource.subject.ilike(like),
            )
        )

    resources = resources_query.order_by(Resource.created_at.desc()).all()
    return render_template(
        "resources/browse.html",
        resources=resources,
        subjects=SUBJECTS,
        selected_subject=subject,
        search_query=query,
    )


@resources_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        subject = request.form.get("subject", "").strip()
        description = request.form.get("description", "").strip()
        resource_type = request.form.get("resource_type", "pdf")

        if not title or not subject:
            flash("Title and subject are required.", "danger")
            return render_template("resources/upload.html", subjects=SUBJECTS)

        resource = Resource(
            title=title,
            subject=subject,
            description=description,
            resource_type=resource_type,
            user_id=current_user.id,
        )

        if resource_type == "link":
            url = request.form.get("url", "").strip()
            if not url:
                flash("URL is required for links.", "danger")
                return render_template("resources/upload.html", subjects=SUBJECTS)
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            resource.url = url
        else:
            file = request.files.get("file")
            if not file or file.filename == "":
                flash("Please select a file to upload.", "danger")
                return render_template("resources/upload.html", subjects=SUBJECTS)
            if not allowed_file(file.filename):
                flash("File type not allowed. Use PDF, TXT, DOC, or DOCX.", "danger")
                return render_template("resources/upload.html", subjects=SUBJECTS)

            filename = secure_filename(file.filename)
            unique_name = f"{current_user.id}_{os.urandom(8).hex()}_{filename}"
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
            file.save(file_path)
            resource.file_path = unique_name
            if resource_type == "pdf" and not filename.lower().endswith(".pdf"):
                resource.resource_type = "note"

        db.session.add(resource)
        db.session.commit()
        flash("Resource uploaded successfully!", "success")
        return redirect(url_for("resources.browse"))

    return render_template("resources/upload.html", subjects=SUBJECTS)


@resources_bp.route("/resource/<int:resource_id>")
def detail(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    return render_template("resources/detail.html", resource=resource)


@resources_bp.route("/download/<int:resource_id>")
def download(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    if resource.is_link:
        return redirect(resource.url)
    if not resource.file_path:
        abort(404)
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        resource.file_path,
        as_attachment=True,
        download_name=resource.file_path.split("_", 2)[-1],
    )
