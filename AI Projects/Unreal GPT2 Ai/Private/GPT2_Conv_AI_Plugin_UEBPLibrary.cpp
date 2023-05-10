// Copyright Wayne Kenney, Wayne.cool, 2023
// All rights reserved

#include "GPT2_Conv_AI_Plugin_UEBPLibrary.h"
#include "GPT2_Conv_AI_Plugin_UE.h"
#include "Blueprint/WidgetBlueprintLibrary.h"
#include "Blueprint/UserWidget.h"
#include "Kismet/GameplayStatics.h"
#include "Components/TextBlock.h"
#include "NPCNameWidget.h"

void UGPT2_Conv_AI_Plugin_UEBPLibrary::ShowNPCName(FString NPC_Name, bool Display_Name, FLinearColor Name_Color, UFont* Name_Font, float Name_Size, FVector2D Name_Offset, float Name_Duration)
{
    APlayerController* PlayerController = UGameplayStatics::GetPlayerController(GWorld, 0);
    if (!PlayerController)
    {
        UE_LOG(LogTemp, Error, TEXT("PlayerController is null."));
        return;
    }

    UClass* WidgetClass = UNPCNameWidget::StaticClass();
    if (!WidgetClass)
    {
        UE_LOG(LogTemp, Error, TEXT("NPCNameWidget class not found."));
        return;
    }

    UNPCNameWidget* NPCNameWidget = CreateWidget<UNPCNameWidget>(PlayerController, WidgetClass);
    if (!NPCNameWidget)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create NPCNameWidget."));
        return;
    }

    UTextBlock* ShowNPCText = NPCNameWidget->ShowNPCText;
    if (!ShowNPCText)
    {
        UE_LOG(LogTemp, Error, TEXT("ShowNPCText is null."));
        return;
    }
    FSlateFontInfo FontInfo;

    ShowNPCText->SetText(FText::FromString(NPC_Name));
    ShowNPCText->SetColorAndOpacity(Name_Color);
    ShowNPCText->SetFont(FontInfo);

    // Set the offset using the desired method

    if (Display_Name)
    {
        NPCNameWidget->AddToViewport();

        if (Name_Duration > 0.0f)
        {
            FTimerHandle TimerHandle;
            PlayerController->GetWorldTimerManager().SetTimer(TimerHandle, NPCNameWidget, &UNPCNameWidget::RemoveFromParent, Name_Duration, false);
        }
    }
}

void UGPT2_Conv_AI_Plugin_UEBPLibrary::UpdateWidgetText(UUserWidget* Widget, const FString& NewText)
{
    if (Widget == nullptr)
    {
        UE_LOG(LogTemp, Error, TEXT("Widget is null."));
        return;
    }

    UTextBlock* TextBlock = Cast<UTextBlock>(Widget->GetWidgetFromName(TEXT("YourTextBlockName")));

    if (TextBlock == nullptr)
    {
        UE_LOG(LogTemp, Error, TEXT("TextBlock not found or is of incorrect type."));
        return;
    }

    TextBlock->SetText(FText::FromString(NewText));
}
