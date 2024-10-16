from syncdog import BSDiffHandler, SyncDogObserver


if __name__ == "__main__":
    source = r"C:\tmp\SyncDogTest"
    dest = r"C:\tmp\SyncDogTest_Dest"

    event_handler = BSDiffHandler(source, dest)
    observer = SyncDogObserver(directory=source, file_handler=event_handler)
    observer.run()
    observer.observer.stop()
    observer.observer.join()
