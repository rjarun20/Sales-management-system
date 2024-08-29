from datetime import datetime

class Client:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.client_id = kwargs.get('client_id')
        self.name = kwargs.get('name')
        self.contact_name = kwargs.get('contact_name')
        self.contact_number = kwargs.get('contact_number')
        self.email = kwargs.get('email')
        self.address_line1 = kwargs.get('address_line1')
        self.address_line2 = kwargs.get('address_line2')
        self.country = kwargs.get('country')
        self.state = kwargs.get('state')
        self.city = kwargs.get('city')
        self.code = kwargs.get('code')
        self.is_deleted = kwargs.get('is_deleted', False)
        self.created_by = kwargs.get('created_by')
        self.updated_by = kwargs.get('updated_by')
        
        # Handle date fields
        self.created_date = self._parse_date(kwargs.get('created_at') or kwargs.get('created_date'))
        self.updated_date = self._parse_date(kwargs.get('updated_at') or kwargs.get('updated_date'))

    def _parse_date(self, date_string):
        if date_string:
            try:
                if isinstance(date_string, str):
                    return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                elif isinstance(date_string, datetime):
                    return date_string
            except ValueError:
                return None
        return None