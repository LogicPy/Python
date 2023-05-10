// Copyright Wayne Kenney, Wayne.cool, 2023
// All rights reserved

#pragma once

#include "Kismet/BlueprintFunctionLibrary.h"
#include "GPT2_Conv_AI_Plugin_UEBPLibrary.generated.h"

UCLASS()
class GPT2_CONV_AI_PLUGIN_UE_API UGPT2_Conv_AI_Plugin_UEBPLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "NPCName")
    static void ShowNPCName(FString NPC_Name, bool Display_Name, FLinearColor Name_Color, UFont* Name_Font, float Name_Size, FVector2D Name_Offset, float Name_Duration);

    UFUNCTION(BlueprintCallable, Category = "NPCName")
    static void UpdateWidgetText(UUserWidget* Widget, const FString& NewText);
};
