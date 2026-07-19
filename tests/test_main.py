from dragverse.__main__ import main


class TestMain:
    def test_main(self, capsys):
        main()
        captured = capsys.readouterr()
        assert captured.out == "DragVerse\n"
