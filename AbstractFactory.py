from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Final


#region Controls
class IButton(ABC):
    @abstractmethod
    def click(self) -> None:
        pass

class ITextBox(ABC):
    text: str

class IOSButton(IButton):
    def click(self) -> None:
        pass

class AndroidButton(IButton):
    def click(self) -> None:
        pass

class IOSTextBox(ITextBox):
    text: str

class AndroidTextBox(ITextBox):
    text: str
#endregion

IsIOS: Final[bool] = ... # Assume this is checked using some API

#region Bad implementation without Abstract Factory   
def bad_main() -> None:
    # Bad: ifs count = #instances of controls => lots of room for human error!
    button1: IButton = IOSButton() if IsIOS else AndroidButton()
    button2: IButton = IOSButton() if IsIOS else AndroidButton()
    textBox1: ITextBox = IOSTextBox() if IsIOS else AndroidTextBox()
#endregion

#region Good implementation using Abstract Factory
def good_main() -> None:
    # Good: just 1 if to choose the control factory
    controlFactory: IControlFactory = IOSControlFactory() if IsIOS else AndroidControlFactory()

    # Somewhere later...
    button1: IButton = controlFactory.create_button()
    button2: IButton = controlFactory.create_button()
    textBox1: ITextBox = controlFactory.create_text_box()

class IControlFactory(ABC):
    @abstractmethod
    def create_button(self) -> IButton:
        pass

    @abstractmethod
    def create_text_box(self) -> ITextBox:
        pass

class IOSControlFactory(IControlFactory):
    def create_button(self) -> IButton:
        return IOSButton()
    def create_text_box(self) -> ITextBox:
        return IOSTextBox()

class AndroidControlFactory(IControlFactory):
    def create_button(self) -> IButton:
        return AndroidButton()
    def create_text_box(self) -> ITextBox:
        return AndroidTextBox()
#endregion
