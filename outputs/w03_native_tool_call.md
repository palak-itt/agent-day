ChatCompletion(
    id='chatcmpl-Edp2wRioOvhb364BQDS2x6IKUGYBB',
    object='chat.completion',
    created=1793159722,
    model='gpt-6-luna',
    service_tier='default',

    choices=[
        Choice(
            index=0,
            finish_reason='tool_calls',

            message=ChatCompletionMessage(
                role='assistant',
                content=None,

                tool_calls=[
                    ChatCompletionMessageFunctionToolCall(
                        id='call_1kgnzJJ1izvLGMpEofG6UTbJ',
                        type='function',

                        function=Function(
                            name='create_ticket',
                            arguments='{"category":"incident","priority":"high"}'
                        )
                    )
                ]
            )
        )
    ],

    usage=CompletionUsage(
        prompt_tokens=183,
        completion_tokens=21,
        total_tokens=204,

        completion_tokens_details=CompletionTokensDetails(
            reasoning_tokens=0,
            audio_tokens=0,
            accepted_prediction_tokens=0,
            rejected_prediction_tokens=0
        ),

        prompt_tokens_details=PromptTokensDetails(
            cached_tokens=0,
            audio_tokens=0,
            image_tokens=None
        )
    )
)

--------

ChatCompletion(id='chatcmpl-EdpJpnGPRPOObUXjZCcZWmWn4QXoK', choices=[Choice(finish_reason='tool_calls', index=0, logprobs=None, message=ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=[ChatCompletionMessageFunctionToolCall(id='call_8pmDKKvlk5GmxBTPSj5cY4GJ', function=Function(arguments='{"category":"incident","priority":"high"}', name='create_ticket'), type='function')]))], created=1793160769, model='gpt-6-luna', object='chat.completion', metadata=None, moderation=None, service_tier='default', system_fingerprint=None, usage=CompletionUsage(completion_tokens=21, prompt_tokens=183, total_tokens=204, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0, text_tokens=None), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cache_write_tokens=0, cached_tokens=0, image_tokens=None, text_tokens=None)))

{'ID': 1888, 'category': 'incident', 'priority': 'high'}
Tool call executed successfully.
ChatCompletion(id='chatcmpl-EdpJrjTykBl5eka3vY5hjkYCTCnC0', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='{"summary":"Login page has been returning 500 errors since this morning, causing lost sales.","category":"incident","priority":"high"}', refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=None))], created=1793160771, model='gpt-6-luna', object='chat.completion', metadata=None, moderation=None, service_tier='default', system_fingerprint=None, usage=CompletionUsage(completion_tokens=30, prompt_tokens=234, total_tokens=264, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0, text_tokens=None), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cache_write_tokens=0, cached_tokens=0, image_tokens=None, text_tokens=None)))

FINAL:  {"summary":"Login page has been returning 500 errors since this morning, causing lost sales.","category":"incident","priority":"high"}