from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return (
        jsonify({"status": "healthy", "service": "GPLv3 Marker Wrapper Isolation API"}),
        200,
    )


@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Mock PDF to Markdown conversion
    pdf_content = file.read()
    mock_markdown = f"""# Converted Document: {file.filename}
    
This is a mock markdown representation of the uploaded PDF file.
Length of processed binary: {len(pdf_content)} bytes.

## Execution Details
- Service: Standalone REST API Container (GPLv3 Isolated)
- Status: Success
"""
    return (
        jsonify(
            {"success": True, "filename": file.filename, "markdown": mock_markdown}
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
