// Function to print the ticket
function printTicket() {
    var ticketContent = document.getElementById('ticket').outerHTML;
    var newWindow = window.open('', '', 'width=800,height=600');
    newWindow.document.write(ticketContent);
    newWindow.document.close();
    newWindow.print();
}

// Function to download the ticket as PDF (you can use jsPDF library)
function downloadPDF() {
    var doc = new jsPDF();
    doc.html(document.getElementById('ticket'), {
        callback: function (doc) {
            doc.save('ticket.pdf');
        }
    });
}
