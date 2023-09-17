// Wayne Kenney 2023

#pragma once

#include "CoreMinimal.h"
#include "Runtime/Online/HTTP/Public/Http.h"
#include "HttpModuleforAi.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAiResponseReceived, const FString&, Response);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnUpdateChatboxText, const FString&, Message);

UCLASS(BlueprintType, Blueprintable)
class GPTAI_API UHttpModuleforAi : public UObject
{
	GENERATED_BODY()

public:
	UHttpModuleforAi();

	UPROPERTY(BlueprintAssignable)
		FOnUpdateChatboxText OnUpdateChatboxText;

	UFUNCTION(BlueprintCallable, Category = "HTTP")
		void SendPostRequest(const FString& Url, const FString& JsonData);

	UFUNCTION(BlueprintImplementableEvent)
		void OnResponseReceivedBP(const FString& responseData);

	UPROPERTY(BlueprintAssignable, Category = "HTTP")
		FOnAiResponseReceived OnAiResponseReceived;

	UFUNCTION(BlueprintCallable, Category = "AI")
		FString GetAiResponseMessage();

	UFUNCTION(BlueprintCallable, Category = "HTTP")
		void SendHttpRequest(const FString& Url, const FString& Verb);

	UFUNCTION(BlueprintCallable, Category = "HTTP")
		FString GetHttpResponse(const FString& JsonResponse);

	UPROPERTY(BlueprintReadWrite, Category = "Widgets")
		class UMyWidget* MyWidget;

	UPROPERTY(BlueprintReadWrite, Category = "HTTP")
		FString AiResponse;  // Declare AiResponse here, added visibility modifier


private:
	FHttpResponsePtr Response;
	FString ResponseString_;
	TOptional<FString> Message;

	void ProcessResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);
	// Handles the response from the server
	void OnResponseReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);
};
