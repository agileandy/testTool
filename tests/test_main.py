from testTool.main import main

def test_main(capsys):
    main()
    captured = capsys.readouterr()
    assert "Hello from testTool!" in captured.out
