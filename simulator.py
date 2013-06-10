from test_elm import MockElm327

def main():
    elm = MockElm327()
    elm.echo = False
    while True:
        data = raw_input()
        elm.write(data + '\r')
        count = 4096
        while count >= 4096:
            write_data = elm.read(4096)
            print write_data.replace('\r', '\n'),
            count = len(write_data)




if __name__ == '__main__':
    main()
