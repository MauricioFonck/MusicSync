"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=32), nullable=False, unique=True),
    )
    op.create_table(
        "tracks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("source_id", sa.String(length=512), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("artist", sa.String(length=512), nullable=False),
        sa.Column("album", sa.String(length=512)),
        sa.Column("album_artist", sa.String(length=512)),
        sa.Column("duration_seconds", sa.String(length=32)),
        sa.Column("track_number", sa.Integer()),
        sa.Column("disc_number", sa.Integer()),
        sa.Column("genre", sa.String(length=255)),
        sa.Column("release_date", sa.Date()),
        sa.Column("thumbnail_url", sa.Text()),
        sa.Column("original_url", sa.Text()),
        sa.UniqueConstraint("source", "source_id", name="uq_tracks_source_source_id"),
    )
    op.create_index("ix_tracks_source", "tracks", ["source"])
    op.create_table(
        "playlists",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("source_id", sa.String(length=512), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("owner", sa.String(length=512)),
        sa.Column("original_url", sa.Text(), nullable=False),
    )
    op.create_table(
        "playlist_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("playlist_id", sa.String(length=36), nullable=False),
        sa.Column("track_id", sa.String(length=36), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.UniqueConstraint("playlist_id", "track_id", name="uq_playlist_items_track"),
    )
    op.create_index("ix_playlist_items_playlist_id", "playlist_items", ["playlist_id"])
    op.create_index("ix_playlist_items_track_id", "playlist_items", ["track_id"])
    op.create_table(
        "storage_devices",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column("volume_label", sa.String(length=255), nullable=False),
        sa.Column("mount_point", sa.Text(), nullable=False),
        sa.Column("filesystem", sa.String(length=64), nullable=False),
        sa.Column("total_space", sa.BigInteger(), nullable=False),
        sa.Column("free_space", sa.BigInteger(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_seen", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "download_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("destination_device_id", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "ix_download_jobs_destination_device_id",
        "download_jobs",
        ["destination_device_id"],
    )
    op.create_index("ix_download_jobs_status", "download_jobs", ["status"])
    op.create_table(
        "download_items",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("track_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text()),
        sa.Column("output_path", sa.Text()),
        sa.Column("checksum", sa.String(length=64)),
    )
    op.create_index("ix_download_items_job_id", "download_items", ["job_id"])
    op.create_index("ix_download_items_track_id", "download_items", ["track_id"])
    op.create_table(
        "download_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("track_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text()),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_download_records_job_id", "download_records", ["job_id"])
    op.create_index("ix_download_records_track_id", "download_records", ["track_id"])
    op.create_table(
        "media_files",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("track_id", sa.String(length=36), nullable=False),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("filename", sa.String(length=512), nullable=False),
        sa.Column("extension", sa.String(length=16), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=False),
        sa.Column("duration_seconds", sa.String(length=32), nullable=False),
        sa.Column("bitrate", sa.Integer()),
        sa.Column("checksum", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_media_files_track_id", "media_files", ["track_id"])
    op.create_index("ix_media_files_checksum", "media_files", ["checksum"])
    op.create_table(
        "settings",
        sa.Column("key", sa.String(length=255), primary_key=True),
        sa.Column("value", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("settings")
    op.drop_index("ix_media_files_checksum", table_name="media_files")
    op.drop_index("ix_media_files_track_id", table_name="media_files")
    op.drop_table("media_files")
    op.drop_index("ix_download_records_track_id", table_name="download_records")
    op.drop_index("ix_download_records_job_id", table_name="download_records")
    op.drop_table("download_records")
    op.drop_index("ix_download_items_track_id", table_name="download_items")
    op.drop_index("ix_download_items_job_id", table_name="download_items")
    op.drop_table("download_items")
    op.drop_index("ix_download_jobs_status", table_name="download_jobs")
    op.drop_index("ix_download_jobs_destination_device_id", table_name="download_jobs")
    op.drop_table("download_jobs")
    op.drop_table("storage_devices")
    op.drop_index("ix_playlist_items_track_id", table_name="playlist_items")
    op.drop_index("ix_playlist_items_playlist_id", table_name="playlist_items")
    op.drop_table("playlist_items")
    op.drop_table("playlists")
    op.drop_index("ix_tracks_source", table_name="tracks")
    op.drop_table("tracks")
    op.drop_table("sources")
