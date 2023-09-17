#pragma once
// Wayne Kenney 2023

#pragma once

#include "CoreMinimal.h"
#include "Components/TextBlock.h"
#include "Blueprint/UserWidget.h"
#include "Components/EditableTextBox.h"
#include "UMyWidget.generated.h"
/**
 * GPTAI_API
 */
UCLASS(BlueprintType)
class GPTAI_API UMyWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    // Other code...
    UPROPERTY(BlueprintReadOnly, meta = (BindWidget), Category = "Widgets")
        class UEditableTextBox* MyEditableTextBox;
    UPROPERTY(BlueprintReadOnly, meta = (BindWidget), Category = "Widgets")
        class UTextBlock* MyTextBlock;
    UPROPERTY(BlueprintReadWrite, Category = "Widgets")
        class UTextBlock* ChatBox;
    UFUNCTION(BlueprintCallable, Category = "AI")
        void UpdateTextBox(const FString& NewText);
    FString AiResponse;
    UFUNCTION(BlueprintCallable, Category = "AI")
        void UpdateTextBlock(const FString& Text, const FString& NewText);


};
