import pyvisual as pv


def create_page_0_ui(window, ui, pila):
    """
    Create and return UI elements for Page 0.
    :param container: The page widget for Page 0.
    :return: Dictionary of UI elements.
    """
    ui_page = {}
    ui_page["Image_0"] = pv.PvImage(container=window, x=-4, y=-31, image_path='assets/images/Imagen_2.png',
        scale=1.164652914395319, corner_radius=0, flip_v=False, flip_h=False,
        rotate=0, border_color=None, border_hover_color=None, on_hover=None,
        on_click=None, on_release=None, border_thickness=0, border_style="solid",
        is_visible=True, opacity=1, tag=None)

    ui_page["Image_1"] = pv.PvImage(container=window, x=10, y=14, image_path='assets/images/Imagen_0.png',
        scale=0.32765036442758205, corner_radius=0, flip_v=False, flip_h=False,
        rotate=0, border_color=None, border_hover_color=None, on_hover=None,
        on_click=None, on_release=None, border_thickness=0, border_style="solid",
        is_visible=True, opacity=1, tag=None)

    ui_page["Button_2"] = pv.PvButton(container=window, x=221, y=14, width=130,
        height=40, text='DETENER', font='Helvetica', font_size=16,
        font_color=(255, 255, 255, 1), font_color_hover=None, bold=False, italic=False,
        underline=False, strikethrough=False, idle_color=(193, 46, 46, 1), hover_color=None,
        clicked_color=None, border_color=(100, 100, 100, 1), border_hover_color=None, border_thickness=0,
        corner_radius=5, border_style="solid", box_shadow=None, box_shadow_hover=None,
        icon_path=None, icon_position='left', icon_color=(255, 255, 255, 1), icon_color_hover=None,
        icon_spacing=0, icon_scale=1, paddings=(0, 0, 0, 0), is_visible=True,
        is_disabled=False, opacity=1, on_hover=None, on_click=None,
        on_release=None, tag=None)

    ui_page["Progressbar_3"] = pv.PvProgressBar(container=window, x=222, y=234, width=96,
        height=35, min_value=0, max_value=100, value= pila,
        track_color=(192, 192, 192, 1), track_border_color=(0, 0, 0, 1), fill_color=(0, 255, 0, 1), track_corner_radius=7,
        opacity=1, idle_color=(255, 255, 255, 0), track_border_thickness=0, scale=1,
        track_height=24, is_circular=False, border_thickness=0, suffix='%',
        font='Helvetica', font_size=12, font_color=(0, 0, 0, 1), font_color_hover=None,
        bold=False, italic=False, underline=False, strikeout=False,
        is_visible=True, is_disabled=False, on_hover=None, on_click=None,
        on_release=None, tag=None)

    ui_page["OpencvImage_10"] = pv.PvOpencvImage(container=window, x=384, y=229, width=298,
        height=169, idle_color=(217, 217, 217, 1), scale=1, corner_radius=10,
        flip_v=False, flip_h=False, rotate=0, border_color=(0, 0, 0, 1),
        border_hover_color=None, border_thickness=0, border_style="solid", is_visible=True,
        fill=True, opacity=1, on_hover=None, on_click=None,
        on_release=None, tag=None)

    ui_page["TextInput_5"] = pv.PvTextInput(container=window, x=222, y=75, width=121,
        height=37, background_color=(255, 255, 255, 1), is_visible=True, placeholder='Q para detener',
        text_alignment='left', default_text='', paddings=(10, 0, 20, 0), font='Helvetica',
        font_size=10, font_color=(0, 0, 0, 1), border_color=(0, 0, 0, 1), border_thickness=1,
        border_style="solid", corner_radius=0, box_shadow='1px 2px 4px 0px rgba(0,0,0,0.2)', icon_path=None,
        icon_scale=1, icon_position='left', icon_spacing=10, icon_color='none',
        text_type='text', max_length=None, on_hover=None, on_click=None,
        on_release=None, tag=None)

    ui_page["Text_6"] = pv.PvText(container=window, x=483, y=-1, width=100,
        height=30, idle_color=(136, 20, 199, 0), text='Mascara', is_visible=True,
        text_alignment='left', paddings=(0, 0, 0, 0), font='Helvetica', font_size=30,
        font_color=(193, 33, 33, 1), bold=False, italic=False, underline=False,
        strikethrough=False, opacity=1, border_color=None, corner_radius=0,
        on_hover=None, on_click=None, on_release=None, tag=None)

    ui_page["Text_7"] = pv.PvText(container=window, x=489, y=194, width=88,
        height=30, idle_color=(136, 20, 199, 0), text='Camara', is_visible=True,
        text_alignment='left', paddings=(0, 0, 0, 0), font='Helvetica', font_size=30,
        font_color=(193, 33, 33, 1), bold=False, italic=False, underline=False,
        strikethrough=False, opacity=1, border_color=None, corner_radius=0,
        on_hover=None, on_click=None, on_release=None, tag=None)

    ui_page["Text_8"] = pv.PvText(container=window, x=255, y=164, width=107,
        height=30, idle_color=(136, 20, 199, 0), text='', is_visible=True,
        text_alignment='left', paddings=(0, 0, 0, 0), font='Helvetica', font_size=30,
        font_color=(193, 33, 33, 1), bold=False, italic=False, underline=False,
        strikethrough=False, opacity=1, border_color=None, corner_radius=0,
        on_hover=None, on_click=None, on_release=None, tag=None)

    ui_page["OpencvImage_11"] = pv.PvOpencvImage(container=window, x=384, y=25, width=298,
        height=169, idle_color=(217, 217, 217, 1), scale=1, corner_radius=10,
        flip_v=False, flip_h=False, rotate=0, border_color=(0, 0, 0, 1),
        border_hover_color=None, border_thickness=0, border_style="solid", is_visible=True,
        fill=True, opacity=1, on_hover=None, on_click=None,
        on_release=None, tag=None)

    ui_page["Image_10"] = pv.PvImage(container=window, x=-320, y=63, image_path='assets/images/1d5f7a2639.svg',
        scale=1.7941176470588236, corner_radius=0, flip_v=False, flip_h=False,
        rotate=0, border_color=None, border_hover_color=None, on_hover=None,
        on_click=None, on_release=None, border_thickness=0, border_style="solid",
        is_visible=True, opacity=1, tag=None)

    ui_page["Text_11"] = pv.PvText(container=window, x=211, y=294, width=119,
        height=55, idle_color=(238, 225, 255, 0), text='Funcionando', is_visible=True,
        text_alignment='left', paddings=(0, 0, 0, 0), font='Helvetica', font_size=31,
        font_color=(103, 174, 79, 1), bold=True, italic=False, underline=False,
        strikethrough=False, opacity=1, border_color=None, corner_radius=0,
        on_hover=None, on_click=None, on_release=None, tag=None)

    ui_page["Image_12"] = pv.PvImage(container=window, x=10, y=214, image_path='assets/images/Imagen_1.png',
        scale=0.32028113331869107, corner_radius=0, flip_v=False, flip_h=False,
        rotate=0, border_color=None, border_hover_color=None, on_hover=None,
        on_click=None, on_release=None, border_thickness=0, border_style="solid",
        is_visible=True, opacity=1, tag=None)

    return ui_page