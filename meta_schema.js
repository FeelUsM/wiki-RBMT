/*
!!! генерация GUI по JSON-схеме - интересная идея
автоматические указатели (абсолютные) - к JSON-схеме не относятся
	после парсинга {$pointer:'address'} превращаются в конкретную ссылку
	перед stringify-кацией неконтролируемым образом циклические ссылки разрываются и превращаются в {$pointer:'address'}
		можно просмотренные объекты/массивы складывать в WeakMap, с путями к ним
	также в этом преобразователе можно задать другое имя свойства (не $pointer)

	валидатор должен быть готов к циклическим структурам
	
ручные указатели - относительные - задаются в схеме
format - задаются в валидаторе: 
	текстовая проверка
	объектная проверка
	преобразование из текста в объект с проверкой
	преобразование из объекта в текст с проверкой
	
равенство - deepEqual
*/
{
	id: "http://json-schema.org/draft-04/schema#",
	$schema: "http://json-schema.org/draft-04/schema#",
	description: "Core schema meta-schema",
	definitions: {
		realSchema: { // !!!! added !!!!, многие { $ref: "#" } заменены на { $ref: "#/definitions/realSchema" }
			oneOf: [
				{ $ref: "#" },
				{
					type: "object",
					requiredProperties: { $ref: { type: "string", format: "json-pointer" } }
				}
			]
		}
		schemaArray: {
			type: "array",
			minItems: 1,
			items: { $ref: "#/definitions/realSchema" }
		},
		positiveInteger: {
			type: "integer",
			minimum: 0
		},
		positiveIntegerDefault0: {
			allOf: [ { $ref: "#/definitions/positiveInteger" }, { default: 0 } ]
		},
		simpleTypes: {
			enum: [ "array", "boolean", "integer", "null", "number", "object", "string",
				"rel_pointer" // !!!! added !!!!
			]
		},
		stringArray: {
			type: "array",
			items: { type: "string" },
			minItems: 1,
			uniqueItems: true
		},
		// !!!! added !!!!
		$data: { // для почти каждого ключевого слова можно вместо его значения предоставить ссылку/указатель на это значение из документа
			type: "object", // объект
			requiredProperties: {
				$data: {
					type: "string",
					format: "relative-json-pointer" // - относительно текущего проверяемого значения
				} 
			},
			"additionalProperties": true
		},
		// === for smth type(s) ===
		forNum: {
			properties: {
				multipleOf: { oneOf: [
					{
						type: "number",
						strictMinimum: 0
					},
					{ $ref: "#/definitions/data"} // !!!! added !!!!
					// в этом случае перед проверкой текущего значения проверяется указываемый этой ссылкой объект,
					// что он число и строго больше 0, и так везде
				]},
				maximum: { oneOf: [
					{
						type: "number"
					},
					{ $ref: "#/definitions/data"} // !!!! added !!!!
				]},
				strictMaximum: { oneOf: [ // !!!! added !!!!
					{
						type: "number"
					},
					{ $ref: "#/definitions/data"}
				]},
				exclusiveMaximum: {
					type: "boolean",
					default: false
				},
				minimum: { oneOf: [
					{
						type: "number"
					},
					{ $ref: "#/definitions/data"} // !!!! added !!!!
				]},
				strictMinimum: { oneOf: [ // !!!! added !!!!
					{
						type: "number"
					},
					{ $ref: "#/definitions/data"}
				]},
				exclusiveMinimum: {
					type: "boolean",
					default: false
				}
			}
		},
		forString: {
			properties: {
				maxLength: { oneOf: [
					{ $ref: "#/definitions/positiveInteger" },
					{ $ref: "#/definitions/data"} // !!!! added !!!!
				]},
				minLength: { oneOf: [
					{ $ref: "#/definitions/positiveIntegerDefault0" },
					{ $ref: "#/definitions/data"} // !!!! added !!!!
				]},
				pattern: { oneOf: [
					{
						type: "string",
						format: "regex"
					},
					{ $ref: "#/definitions/data"} // !!!! added !!!!
				]}
			}
		},
		forArray: {
			properties: {
				uniqueItems: {
					type: "boolean",
					default: false
				},
				items: {
					anyOf: [
						{ $ref: "#/definitions/realSchema" },
						{ $ref: "#/definitions/schemaArray" }
					],
					default: {}
				},
				additionalItems: {
					anyOf: [
						{ type: "boolean" },
						{ $ref: "#/definitions/realSchema" }
					],
					default: false // !!!! modified !!!!
				},
				maxItems: { $ref: "#/definitions/positiveInteger" },
				minItems: { $ref: "#/definitions/positiveIntegerDefault0" },
				contain: { // !!!! added !!!!
					type: "array",
					minItems: 1,
					uniqueItems: true
				}
			}
		},
		forObject: {
			properties: {
				required: { $ref: "#/definitions/stringArray" },
				requiredProperties: { // !!!! added !!!!
					type: "object",
					additionalProperties: { $ref: "#/definitions/realSchema" },
					default: {}
				},
				properties: {
					type: "object",
					additionalProperties: { $ref: "#/definitions/realSchema" },
					default: {}
				},
				patternProperties: {
					type: "object",
					additionalProperties: { $ref: "#/definitions/realSchema" },
					default: {}
				},
				additionalProperties: {
					anyOf: [
						{ type: "boolean" },
						{ $ref: "#/definitions/realSchema" }
					],
					default: false // !!!! changed !!!!
				},
				maxProperties: { $ref: "#/definitions/positiveInteger" },
				minProperties: { $ref: "#/definitions/positiveIntegerDefault0" },
				dependencies: {
					type: "object",
					additionalProperties: {
						anyOf: [
							{ $ref: "#/definitions/realSchema" },
							{ $ref: "#/definitions/stringArray" }
						]
					}
				}
			},
			dependencies: {
				pointerAt: [ "minSearchDepth", "maxSearchDepth" ], // !!!! added !!!!
				exclusiveMaximum: [ "maximum" ],
				exclusiveMinimum: [ "minimum" ]
			}
		},
		forArrayOrObject: { // !!!! added !!!!
			properties: {
				additionalAllOf: { $ref: "#/definitions/schemaArray" },
				additionalAnyOf: { $ref: "#/definitions/schemaArray" },
				additionalOneOf: { $ref: "#/definitions/schemaArray" },
				/* !!!!
					три свойства выше:
					перед проверкой на additionalProperties или additionalItems текущей схемы
					проверяются схемы, перечисленные здесь
						внутри них additionalProperties или additionalItems - true
						при возвращени - items, requiredProperties, properties и patternProperties и required
						объединяются с текущими,
					после чего производится проверка на на additionalProperties или additionalItems текущей схемы
					todo: придумать и записать алгоритм преобразования этой байды в allOf, anyOf и oneOf
						items, requiredProperties, properties и patternProperties и required
						 - перемещаются (и копируется) в каждый элемент, и объединяется с имеющимися
						если схема назначения - ссылка, то она копируется
						остальные свойства - перемещаются с заменой
						это прокатит только с OneOf
						AllOf - можно объединить в один, и там не важно, allOf или oneOf
						AnyOf - можно переделать в 2^n случаев oneOf и объединений
						помимо того, что это просто не эффективно, объединение схем потребует интеллектуальных усилий, а это еще огрмная куча разных вариантов
						=> все должно реализовываться вручную:
						
						внутри схем внутри additionalSmthOf additionalProperties или additionalItems по умолчанию true
						а также каждая схема (после собственной валидации) возвращает набор проверенных свойств
							(за счет items (если массив), requiredProperties, properties и patternProperties и required)
						после чего выполняется additionalProperties или additionalItems корневой схемы
						но, additionalOneOf определяет удачность варианта только вместе с 
							additionalProperties или additionalItems корневой схемы
				*/
			}
		},
	},
	type: "object",
	properties: {
	//{ === общие === 
		id: {
			type: "string",
			format: "uri"
		},
		$schema: {
			type: "string",
			format: "uri"
		},
		title: {
			type: "string"
		},
		description: {
			type: "string"
		},
		definitions: {
			type: "object",
			additionalProperties: { $ref: "#" },
			default: {}
		},
	//}
	//{ === для любых типов === 
		allOf: { $ref: "#/definitions/schemaArray" },
		anyOf: { $ref: "#/definitions/schemaArray" },
		oneOf: { $ref: "#/definitions/schemaArray" },
		not: { $ref: "#/definitions/realSchema" },
		enum: {
			type: "array",
			minItems: 1,
			uniqueItems: true
		},
		equal: { "$ref": "#/definitions/$data" }, // !!!! added !!!!
		format: { // !!!! addition !!!!
			type: "string",
			enum: [
				"relative-json-pointer", // /^\d*(\/.*)?$/
				"json-pointer", // /^([_a-zA-Z][-_a-zA-Z0-9]*)?(#(\/.*)?)?$/
				"regex", // отсутствует в jjv
				"alpha", // /^[a-zA-Z]+$/
				"alphanumeric", // /^[a-zA-Z0-9]+$/
				"identifier", // /^[_a-zA-Z][-_a-zA-Z0-9]*$/
				"hexadecimal", // /^[a-fA-F0-9]+$/
				"numeric", // /^[0-9]+$/
				"date-time", // v=> !isNaN(Date.parse(v)) && v.indexOf('/') === -1
				"uppercase", // v=> v === v.toUpperCase()
				"lowercase", // v=> v === v.toLowerCase()
				"hostname", // /^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*$/ и длина меньше 256 символов
				"uri", // /[-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?/
				"email", // /^(?:[\w\!\#\$\%\&\'\*\+\-\/\=\?\^\`\{\|\}\~]+\.)*[\w\!\#\$\%\&\'\*\+\-\/\=\?\^\`\{\|\}\~]+@(?:(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-](?!\.)){0,61}[a-zA-Z0-9]?\.)+[a-zA-Z0-9](?:[a-zA-Z0-9\-](?!$)){0,61}[a-zA-Z0-9]?)|(?:\[(?:(?:[01]?\d{1,2}|2[0-4]\d|25[0-5])\.){3}(?:[01]?\d{1,2}|2[0-4]\d|25[0-5])\]))$/
				"ipv4", // /^(\d?\d?\d)\.(\d?\d?\d)\.(\d?\d?\d)\.(\d?\d?\d)$/ и последнее число<=255
				"ipv6" // /^((?=.*::)(?!.*::.+::)(::)?([\dA-F]{1,4}:(:|\b)|){5}|([\dA-F]{1,4}:){6})((([\dA-F]{1,4}((?!\3)::|:\b|$))|(?!\2\3)){2}|(((2[0-4]|1\d|[1-9])?\d|25[0-5])\.?\b){4})$/
			]
		},
		default: {},
		// + при разборе дописывает, а при stringify-кации - если равно, удаляет
	//}
	//{ === относительные указатели === // !!!! added !!!!
		instanceOf: { format: "json-pointer" }, // то же самое, что и pointerAt, при searechDepth: 1
		pointerAt: { format: "json-pointer" },
		minSearchDepth: {
			type: "integer",
			minimum: 0
		}
		maxSearchDepth: {
			type: "integer",
			minimum: { $data: "../minSearchDepth" }
		}
		/* !!!!
			проверяет, есть ли значение, по адрусу документа, относительно адреса схемы
			при разборе - за О(1)
			при stringify-кации - производит поиск заданной глубины
		*/
	//}
	},
	dependencies: {
		pointerAt: [ "minSearchDepth", "maxSearchDepth" ] // !!!! added !!!!
	}
	additionalOneOf: [
		{	additionalAnyOf: [ // если type не указан, можно писать что угодно
				{ $ref: "#/definitions/forNum" },
				{ $ref: "#/definitions/forString" },
				{ $ref: "#/definitions/forArray" },
				{ $ref: "#/definitions/forObject" },
				{ $ref: "#/definitions/forArrayOrObject" }
			]
		},
		{	additionalAnyOf: [ // если type указан и чего-то не содержит, то об этом писать нельзя
				{ // "boolean", "null"
					requiredProperties: {
						type: {
							anyOf: [
								{ enum: [ "boolean", "null" ] },
								{
									type: "array",
									items: { $ref: "#/definitions/simpleTypes" },
									minItems: 1,
									uniqueItems: true,
									contain: [ "boolean", "null" ]
								}
							]
						}
					}
				},
				{ // "integer", "number"
					requiredProperties: {
						type: {
							anyOf: [
								{ enum: [ "integer", "number" ] },
								{
									type: "array",
									items: { $ref: "#/definitions/simpleTypes" },
									minItems: 1,
									uniqueItems: true,
									contain: [ "integer", "number" ]
								}
							]
						}
					},
					additiionalAllOf: [ { $ref: "#/definitions/forNum" } ]
				},
				{ // "string"
					requiredProperties: {
						type: {
							anyOf: [
								{ enum: [ "string" ] },
								{
									type: "array",
									items: { $ref: "#/definitions/simpleTypes" },
									minItems: 1,
									uniqueItems: true,
									contain: [ "string" ]
								}
							]
						}
					},
					additiionalAllOf: [ { $ref: "#/definitions/forString" } ]
				},
				{ // "array"
					requiredProperties: {
						type: {
							anyOf: [
								{ enum: [ "array" ] },
								{
									type: "array",
									items: { $ref: "#/definitions/simpleTypes" },
									minItems: 1,
									uniqueItems: true,
									contain: [ "array" ]
								}
							]
						}
					},
					additiionalAllOf: [ { $ref: "#/definitions/forArray" } ]
				},
				{ // "object"
					requiredProperties: {
						type: {
							anyOf: [
								{ enum: [ "object" ] },
								{
									type: "array",
									items: { $ref: "#/definitions/simpleTypes" },
									minItems: 1,
									uniqueItems: true,
									contain: [ "object" ]
								}
							]
						}
					},
					additiionalAllOf: [ { $ref: "#/definitions/forObject" } ]
				},
				{ // "array", "object"
					requiredProperties: {
						type: {
							anyOf: [
								{ enum: [ "array", "object" ] },
								{
									type: "array",
									items: { $ref: "#/definitions/simpleTypes" },
									minItems: 1,
									uniqueItems: true,
									contain: [ "array", "object" ]
								}
							]
						}
					},
					additiionalAllOf: [ { $ref: "#/definitions/forArrayOrObject" } ]
				}
			]
		}
	],
	default: {}
}
