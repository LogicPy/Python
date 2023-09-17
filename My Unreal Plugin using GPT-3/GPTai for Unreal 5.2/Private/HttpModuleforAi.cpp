// Wayne Kenney 2023

#include "HttpModuleforAi.h"
#include "Runtime/Online/HTTP/Public/Http.h"
#include "HttpModuleforAi.h"
#include "HttpModule.h"
#include "Json.h"
#include <typeinfo>
#include <iostream>
#include <string>
#include "Misc/AssertionMacros.h"

DEFINE_LOG_CATEGORY_STATIC(MyLogCategory, Log, All);

void UHttpModuleforAi::SendHttpRequest(const FString& Url, const FString& Verb)
{
    TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request = FHttpModule::Get().CreateRequest();
    Request->SetURL(Url);
    Request->SetVerb(Verb);

    Request->OnProcessRequestComplete().BindUObject(this, &UHttpModuleforAi::OnResponseReceived);

    Request->ProcessRequest();
}

void UHttpModuleforAi::SendPostRequest(const FString& Url, const FString& JsonData)
{
    TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request = FHttpModule::Get().CreateRequest();
    Request->OnProcessRequestComplete().BindUObject(this, &UHttpModuleforAi::OnResponseReceived);

    //This is the url on which to process the request
    Request->SetURL(Url);
    Request->SetVerb("POST");
    Request->SetHeader(TEXT("User-Agent"), "X-UnrealEngine-Agent");
    Request->SetHeader("Content-Type", TEXT("application/json"));
    Request->SetContentAsString(JsonData);

    // Execute the request
    Request->ProcessRequest();
}

void UHttpModuleforAi::OnResponseReceived(FHttpRequestPtr Request, FHttpResponsePtr HttpResponse, bool bWasSuccessful)
{
    UE_LOG(LogTemp, Warning, TEXT("OnResponseReceived called."));

    // Check if the Response is valid

    UE_LOG(LogTemp, Warning, TEXT("Response is valid before GetHttpResponse: 1"));

    FString ResponseStr = HttpResponse->GetContentAsString();
    //GEngine->AddOnScreenDebugMessage(-1, 15.0f, FColor::Yellow, FString::Printf(TEXT("%s = StringVariable"), *ResponseStr));
    UE_LOG(LogTemp, Warning, TEXT("Response is valid."));
    UE_LOG(LogTemp, Warning, TEXT("Response code is OK."));
    UE_LOG(LogTemp, Warning, TEXT("Json Response: %s"), *ResponseStr);


    //...
  // Create a JSON object to hold the parsed data
    TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject());

    // Create a reader for the JSON data
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(ResponseStr);

    // Use the JsonObjectStringToUStruct function to convert the string to a JSON object
    if (FJsonSerializer::Deserialize(Reader, JsonObject) && JsonObject.IsValid())
    {
        // Get the "message" object
        TSharedPtr<FJsonObject> MessageObject = JsonObject->GetObjectField("message");

        // Get the "choices" array
        TArray<TSharedPtr<FJsonValue>> ChoicesArray = MessageObject->GetArrayField("choices");

        // Get the first object in the array
        TSharedPtr<FJsonObject> ChoicesObject = ChoicesArray[0]->AsObject();

        // Get the "message" object inside the "choices" object
        TSharedPtr<FJsonObject> InnerMessageObject = ChoicesObject->GetObjectField("message");

        // Now get the "content" string
        FString MessageContent = InnerMessageObject->GetStringField("content");

        // Print the message content
        UE_LOG(LogTemp, Warning, TEXT("Message Content: %s"), *MessageContent);

        // For final response printing in Unreal's UI after response is extracted from JSON
        OnUpdateChatboxText.Broadcast(MessageContent);
    }




    //GEngine->AddOnScreenDebugMessage(-1, 15.0f, FColor::Yellow, ResponseStr);
    // This line broadcasts the message to any functions that are bound to OnUpdateChatboxText





}

UHttpModuleforAi::UHttpModuleforAi()
{
    // Constructor implementation...
}

FString UHttpModuleforAi::GetAiResponseMessage()
{
    if (Message.IsSet())
    {
        return Message.GetValue();
    }
    return TEXT("");
}

void UHttpModuleforAi::ProcessResponse(FHttpRequestPtr Request, FHttpResponsePtr varResponse, bool bWasSuccessful)
{
    if (Response.IsValid() && EHttpResponseCodes::IsOk(Response->GetResponseCode()))
    {

        if (bWasSuccessful)
        {
            FString responseData = Response->GetContentAsString();
        }

    }
    else
    {

    }
    this->Response.Reset();
}

FString UHttpModuleforAi::GetHttpResponse(const FString& JsonResponse)
{
    // Initialize an empty FJsonObject pointer
    TSharedPtr<FJsonObject> jsonObject = MakeShareable(new FJsonObject());

    // Create a JsonReader with the JsonResponse
    TSharedRef<TJsonReader<>> reader = TJsonReaderFactory<>::Create(JsonResponse);
    UE_LOG(LogTemp, Warning, TEXT("JSON Response0: %s"), *Response->GetContentAsString());
    // Check if the JsonResponse can be deserialized to a JSON object
    if (FJsonSerializer::Deserialize(reader, jsonObject) && jsonObject.IsValid())
    {
        // Log the success
        UE_LOG(LogTemp, Warning, TEXT("Json Response2: %s"), *JsonResponse);

        // Check if the JSON object has the field "message"
        if (jsonObject->HasTypedField<EJson::String>("message"))
        {
            // Existing code
            UE_LOG(LogTemp, Warning, TEXT("Found message field."));

            // Access the "message" field
            FString message = jsonObject->GetStringField("message");

            // Log the message
            UE_LOG(LogTemp, Warning, TEXT("Message: %s"), *message);

            // Return the message
            return message;
        }
        OnResponseReceivedBP(Message.GetValue());
    }
    else
    {
        // Log the failure
        UE_LOG(LogTemp, Error, TEXT("Failed to parse JSON response: %s"), *JsonResponse);
    }

    // Return an empty string if there was an issue
    return "";
}
