from webcrawlers import NBAScraping

def main():
    download = NBAScraping(
        url='https://www.lojanba.com/'
    )
    
    download.extract_data()

if __name__ == '__main__':
    main()