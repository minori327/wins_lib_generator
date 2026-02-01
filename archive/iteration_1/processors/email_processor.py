"""
Extract headers and body from email files mechanically.
"""

import email
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_email_data(file_path: Path) -> Dict[str, Any]:
    """Extract headers and body from email file.

    Args:
        file_path: Path to .eml file

    Returns:
        Dictionary with keys:
        - subject: str - Email subject
        - from: str - From address
        - to: str - To addresses
        - cc: str - CC addresses (if present)
        - date: str - Date string
        - body: str - Email body content

    Raises:
        FileNotFoundError: If email file does not exist
        ValueError: If email parsing fails
    """
    if not file_path.exists():
        logger.error(f"Email file does not exist: {file_path}")
        raise FileNotFoundError(f"Email file does not exist: {file_path}")

    try:
        with open(file_path, 'rb') as file:
            msg = email.message_from_binary_file(file)

        # Extract headers
        subject = msg.get('subject', '')
        from_addr = msg.get('from', '')
        to_addr = msg.get('to', '')
        cc_addr = msg.get('cc', '')
        date_str = msg.get('date', '')

        # Extract body
        body = ''
        if msg.is_multipart():
            # Handle multipart messages
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition', ''))

                # Extract text/plain parts
                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            # Try to decode with charset from part
                            charset = part.get_content_charset() or 'utf-8'
                            body = payload.decode(charset, errors='replace')
                            break
                    except Exception as e:
                        logger.warning(f"Failed to decode email part: {e}")
                        continue
        else:
            # Handle simple (non-multipart) messages
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or 'utf-8'
                    body = payload.decode(charset, errors='replace')
            except Exception as e:
                logger.warning(f"Failed to decode email body: {e}")
                body = str(msg.get_payload())

        email_data = {
            'subject': subject,
            'from': from_addr,
            'to': to_addr,
            'cc': cc_addr,
            'date': date_str,
            'body': body,
        }

        logger.info(f"Extracted email data from {file_path}: subject='{subject[:50]}...', from={from_addr}")

        return email_data

    except email.errors.MessageParseError as e:
        logger.error(f"Failed to parse email file {file_path}: {e}")
        raise ValueError(f"Failed to parse email: {e}")
    except Exception as e:
        logger.error(f"Failed to read email file {file_path}: {e}")
        raise ValueError(f"Failed to extract email data: {e}")
