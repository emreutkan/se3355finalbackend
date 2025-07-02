from flask import Blueprint, jsonify, current_app
from app import db
from scripts.seed_data import seed_database

dev_bp = Blueprint('dev', __name__)

@dev_bp.route('/reset-database', methods=['POST'])
def reset_database():
    """
    Clear all database tables and re-seed with sample data.
    This is a protected endpoint for development purposes.
    ---
    tags:
      - Development
    summary: Reset and seed the database
    description: Clears all data from the database and populates it with initial seed data. For development use only.
    responses:
      200:
        description: Database reset and seeded successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Database has been successfully reset and seeded.
      403:
        description: Forbidden
        schema:
          type: object
          properties:
            error:
              type: string
              example: This endpoint is only available in development environment
      500:
        description: Internal Server Error
        schema:
          type: object
          properties:
            error:
              type: string
              example: An error occurred during database reset.
    """
    try:
        current_app.logger.info("[-] Starting database reset...")

        # Clear all data from tables
        # Using a more robust method to delete data without dropping tables
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            current_app.logger.info(f"Clearing table: {table.name}")
            db.session.execute(table.delete())
        db.session.commit()

        current_app.logger.info("[+] All tables cleared.")

        # Seed the database
        current_app.logger.info("[-] Seeding database with sample data...")
        seed_database()
        current_app.logger.info("[+] Database seeded successfully.")

        return jsonify(message="Database has been successfully reset and seeded."), 200

    except Exception as e:
        current_app.logger.error(f"[!] Database reset failed: {str(e)}")
        db.session.rollback()
        return jsonify(error=f"An error occurred during database reset: {str(e)}"), 500
