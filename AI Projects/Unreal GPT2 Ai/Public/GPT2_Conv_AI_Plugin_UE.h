// Copyright Wayne Kenney, Wayne.cool, 2023
// All rights reserved

#pragma once

#include "Modules/ModuleManager.h"

class FGPT2_Conv_AI_Plugin_UEModule : public IModuleInterface
{
public:

	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
};
