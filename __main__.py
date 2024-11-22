if __name__ == "__main__":
    from src import init
    from src import State

    scheme = init()
    print(scheme.structure_str(short=True))
    scheme.run(State())
