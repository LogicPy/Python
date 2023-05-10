// Copyright Wayne Kenney, Wayne.cool, 2023
// All rights reserved

#include "GPT2_Conv_AI_Plugin_UE.h"

#define LOCTEXT_NAMESPACE "FGPT2_Conv_AI_Plugin_UEModule"

void FGPT2_Conv_AI_Plugin_UEModule::StartupModule()
{
	// This code will execute after your module is loaded into memory; the exact timing is specified in the .uplugin file per-module
	
}

void FGPT2_Conv_AI_Plugin_UEModule::ShutdownModule()
{
	// This function may be called during shutdown to clean up your module.  For modules that support dynamic reloading,
	// we call this function before unloading the module.
	
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FGPT2_Conv_AI_Plugin_UEModule, GPT2_Conv_AI_Plugin_UE)