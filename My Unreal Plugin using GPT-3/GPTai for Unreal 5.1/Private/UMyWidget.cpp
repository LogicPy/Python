// Wayne Kenney 2023

#include "UMyWidget.h"
#include "Blueprint/UserWidget.h"
#include "Components/TextBlock.h"
#include "Components/EditableTextBox.h"

void UMyWidget::UpdateTextBlock(const FString& Text, const FString& NewText)
{
    if (MyTextBlock)
    {
        MyTextBlock->SetText(FText::FromString(Text));
    }
}
void UMyWidget::UpdateTextBox(const FString& NewText)
{
    if (MyEditableTextBox)
    {
        MyEditableTextBox->SetText(FText::FromString(NewText));
    }
}
