"""CineFlix - ponto de entrada do aplicativo.

Execute com:  python main.py
"""

from dados import Catalogo
from interface import AppCineFlix


def main():
    app = AppCineFlix(Catalogo())
    app.mainloop()  # entrega o controle ao Tkinter, que passa a esperar eventos


if __name__ == "__main__":
    main()
