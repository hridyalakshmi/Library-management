import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus


class LibraryTransaction(Document):
    def before_submit(self):
        if self.type == "Issue":
            self.validate_issue()
            self.update_article_list()
            for row in self.article_list:
                article = frappe.get_doc("Article", row.article)
                article.status = "Issued"
                article.save()

        elif self.type == "Return":
            self.validate_return()
            self.remove_articles()
            for row in self.article_list:
                article = frappe.get_doc("Article", row.article)
                article.status = "Available"
                article.save()



    def validate_issue(self):
        self.validate_membership()
        article = frappe.get_doc("Article", self.article)
        # article cannot be issued if it is already issued
        if article.status == "Issued":
            frappe.throw("Article is already issued by another member")

    def before_save(self):
        if self.type == "Return":
            self.validate_return()

    def validate_return(self):
        for row in self.article_list:
            article = frappe.get_doc("Article", row.article)
            if article.status == "Available":
                frappe.throw("Article cannot be returned without being issued first")


    def remove_articles(self):
    # Fetch the Library Member document
        library_member = frappe.get_doc("Library Member", self.library_member)

    # Check if the document was found
        if library_member:
            articles_found = False
        # Create a list of articles to remove
            articles_to_remove = [row.article for row in self.article_list]

        # Iterate through the "issued_articles" child table entries
            issued_articles = library_member.get("issued_articles")
            for article_entry in list(issued_articles):
                if article_entry.article_name in articles_to_remove:
                # Remove the article entry from the "issued_articles" child table
                    issued_articles.remove(article_entry)
                    articles_found = True

            if articles_found:
            # Save the updated Library Member document
                library_member.save()
                frappe.msgprint("Articles returned successfully.")
            else:
                frappe.msgprint("Articles not found in the library member's issued articles list.")
        else:
            frappe.throw("Library Member not found")




    # def validate_return(self):
    #     # article = frappe.get_doc("Article", self.article)
    #     article = frappe.get_doc("Article", self.article)
    #     # article cannot be returned if it is not issued first
    #     if article.status == "Available":
    #         frappe.throw("Article cannot be returned without being issued first")

    def validate_membership(self):
        # check if a valid membership exist for this library member
        valid_membership = frappe.db.exists(
            "Library Membership",
            {
                "library_member": self.library_member,
                "docstatus": 1,
                "from_date": ("<", self.date),
                "to_date": (">", self.date),
            },
        )
        if not valid_membership:
            frappe.throw("The member does not have a valid membership")

    # def before_save(self):
    #     if self.type == "Return":
    #         self.validate_return()
    #         self.calc_delay_fine()
    #         damage_fine = int(self.damage_fine) if self.damage_fine else 0
    #         self.total_fine = self.delay_fine + damage_fine


    # def before_save(self):
    #     if self.type == "Return":
    #         self.validate_return()
    #         self.calculate_fines()
    #
    # def calculate_fines(self):
    #     self.delay_fine = self.calc_delay_fine() or 0
    #     damage_fine = int(self.damage_fine) if self.damage_fine else 0
    #     self.total_fine = self.delay_fine + damage_fine
    #
    # def calc_delay_fine(self):
    #     total_delay_fine = 0
    #     loan_period = frappe.db.get_single_value('Library Settings', 'loan_period')
    #     single_day_fine = frappe.db.get_single_value('Library Settings', 'single_day_fine')
    #
    #     for row in self.article_list:
    #         issued_doc = frappe.get_last_doc(
    #             "Library Transaction",
    #             filters={
    #                 "library_member": self.library_member,
    #                 "article": row.article,
    #                 "docstatus": 1,
    #                 "type": "Issue",
    #             },
    #             order_by="creation DESC"  # Specify the table name for the 'creation' column
    #         )
    #         if issued_doc:
    #             issued_date = issued_doc.date
    #             actual_duration = date_diff(self.date, issued_date)
    #
    #             if actual_duration > loan_period:
    #                 delay_fine = single_day_fine * (actual_duration - loan_period)
    #                 row.delay_fine = delay_fine
    #                 total_delay_fine += delay_fine
    #             else:
    #                 row.delay_fine = 0
    #
    #     return total_delay_fine



    def before_save(self):
        if self.type == "Return":
            self.validate_return()
            self.delay_fine = self.calc_delay_fine() or 0  # Assign 0 if self.delay_fine is None
            damage_fine = int(self.damage_fine) if self.damage_fine else 0
            self.total_fine = self.delay_fine + damage_fine

    def calc_delay_fine(self):
        for row in self.article_list:
            valid_delay_fine = frappe.db.exists(
            "Library Transaction",
            {
                "library_member": self.library_member,
                "article": row.article,
                "docstatus": 1,
                "type": "Issue",
            },
        )

            if valid_delay_fine:
                issued_doc = frappe.get_last_doc(
                    "Library Transaction",
                    filters={
                        "library_member": self.library_member,
                        "article": row.article,
                        "docstatus": 1,
                        "type": "Issue",
                    },
            )
                issued_date = issued_doc.date

                loan_period = frappe.db.get_single_value('Library Settings', 'loan_period')
                actual_duration = frappe.utils.date_diff(self.date, issued_date)

                if actual_duration > loan_period:
                    single_day_fine = frappe.db.get_single_value('Library Settings', 'single_day_fine')
                    row.delay_fine = single_day_fine * (actual_duration - loan_period)
                else:
                    row.delay_fine = 0
            else:
                row.delay_fine = 0

    def update_article_list(self):
    # Fetch the Library Member document
        library_member = frappe.get_doc("Library Member", self.library_member)

    # Iterate through article_list and add issued articles to issued_articles
        if self.type == "Issue":
            for row in self.article_list:
                library_member.append("issued_articles", {
                    "article_name": row.article,
                # Add any other necessary fields here, such as issue_date or due_date
                })

    # Save the updated Library Member document
        library_member.save()

        # Optionally, return a success message
        #     return "Article list updated successfully."
        # except Exception as e:
        # # Handle any errors that occur during the process
        #     frappe.log_error(f"Error updating article list: {str(e)}")
        #     frappe.throw("An error occurred while updating the article list.")

    # def get_table_field_doctype(self, fieldname):
    #     field = self.meta.get_field(fieldname)
    #
    #     if field:
    #         if hasattr(field, 'options'):
    #             return field.options
    #         else:
    #             frappe.throw(f"Field '{fieldname}' does not have 'options' attribute.")
    #     else:
    #         frappe.throw(f"Field '{fieldname}' not found.")



    def validate_issue(self):
    # Validate membership
        self.validate_membership()
        issued_count = []
    # ck maximum number of issued articles
        for row in self.article_list:
            issued_count.append(len(self.article_list))

    # Check maximum number of issued articles
        issued_articles = frappe.db.get_single_value('Library Settings', 'issued_articles')
        issued_count = frappe.db.count('Library Transaction', {'library_member': self.library_member, 'type': 'Issue', 'docstatus': 1})
        if issued_count >= issued_articles:
            frappe.throw('The member has already reached the maximum number of issued articles')

    # Check if the article is already issued
        for row in self.article_list:
            article = frappe.get_doc('Article', row.article)
            if article.status == 'Issued':
                frappe.throw(f'Article {article.name} is already issued by another member')


    # def validate_issue(self):
    # # Validate membership
    #     self.validate_membership()
    #
    #     for article in self.article_list:
    #         article = frappe.get_doc("Article", article.article)
    #
    #         if article.status == "Issued":
    #             frappe.throw(f"Article {article.name} is already issued by another member")
    #



    # python method signature
    # def custom_query(Library_Transaction, article, Status, start, end, Available):
    # # your logic here
    #     filtered_list = []  # initialize an empty list to store filtered results
    #     for transaction in Library_Transaction:
    # # apply your filtering conditions here
    #         if transaction.article == article and transaction.Status == Status and start <= transaction.date <= end and transaction.Available == Available:
    #             filtered_list.append(transaction)  # add matching transactions to the filtered list
    #             return filtered_list
