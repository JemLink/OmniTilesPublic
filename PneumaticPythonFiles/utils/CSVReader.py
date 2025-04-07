from csv import DictReader


def getRowsOfFile(fileName):
    returnRows = []
    with open(fileName, 'r') as file:
        csv_reader = DictReader(file)
        for row in csv_reader:
            arr = list(map(int, row['Array'].split(",")))
            returnRows.append([int(row['ID']), arr])
    return returnRows

