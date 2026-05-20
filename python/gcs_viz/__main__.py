import sys


def main():
    if "--gui" in sys.argv or "--tk" in sys.argv:
        from gcs_viz.platform_gui import main as gui_main
        gui_main()
    else:
        from gcs_viz.platform_gui import main as gui_main
        gui_main()


if __name__ == "__main__":
    main()
