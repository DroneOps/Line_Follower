import pyvisual as pv
from creacion_imagen import create_page_0_ui


def create_window():
    window = pv.PvWindow(
        title="PyVisual Window",
        width=700,
        height=400,
        bg_color=(255, 255, 255, 0.99),
        icon=None,
        bg_image=None,
        is_frameless=False,
        is_resizable=False
    )
    return window


def create_pages(window):
    pages = pv.PvPages(window, animation_duration=0, animation_orientation="horizontal")
    page_0 = pages.create_page("page_0",   bg_color=(255, 255, 255, 0.99),  bg_image=None)
    return pages, page_0


def create_ui(pila):
    window = create_window()
    pages, page_0 = create_pages(window)
    page_0_widget = pages.widget(page_0)
    ui = {
        "window": window,
        "pages": pages
    }
    ui_page_0 = create_page_0_ui(page_0_widget, ui, pila)

    ui.update({
        "page_0": ui_page_0
    })

    return ui

def button_clicked(instance):
    print("ia voy")

def binding(ui):
    ui['page_0']['Button_2'].on_click = button_clicked

def main():
    app = pv.PvApp()
    ui = create_ui()
    binding(ui)
    ui["window"].show()
    print(type(app))
    print(type(ui["window"]))
    app.run()


if __name__ == "__main__":
    main()
