// Copyright Wayne Kenney, Wayne.cool, 2023
// All rights reserved

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Components/TextBlock.h"
#include "NPCNameWidget.generated.h"

UCLASS()
class GPT2_CONV_AI_PLUGIN_UE_API  UNPCNameWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, Category = "NPC Name Widget", meta = (BindWidget))
    UTextBlock* ShowNPCText;
};
