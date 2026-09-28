from dados import Catalogo
from interface import AppCineFlix


def main():
    app = AppCineFlix(Catalogo())
    app.mainloop()


if __name__ == "__main__":
    main()
