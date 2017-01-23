import db


def submissionProcessed(id_value):
    data = {
        'id' : id_value,
        'processed' : 1
    }

    db.updateSubmission(data)

def submissionSuccess(id_value):
    data = {
        'id' : id_value,
        'failed' : 1
    }

    db.updateSubmission(data)
