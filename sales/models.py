class Client:
    def __init__(self, id, client_id, name, contact_name, contact_number, email, address_line1, address_line2, country, state, city, code, is_deleted, created_by, created_date, updated_by, updated_date):
        self.id = id
        self.client_id = client_id
        self.name = name
        self.contact_name = contact_name
        self.contact_number = contact_number
        self.email = email
        self.address_line1 = address_line1
        self.address_line2 = address_line2
        self.country = country
        self.state = state
        self.city = city
        self.code = code
        self.is_deleted = is_deleted
        self.created_by = created_by
        self.created_date = created_date
        self.updated_by = updated_by
        self.updated_date = updated_date