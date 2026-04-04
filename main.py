from webcrawlers import NBAScraping

def main():

    print("Iniciando scraping...")
    download = NBAScraping(
        url='https://www.lojanba.com'
    )

    download.extract_data()

    download.analyze_data()

    download.clean_data()

    download.upload_product()

if __name__ == '__main__':
    main()