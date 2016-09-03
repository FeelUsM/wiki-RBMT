var schemas;
if(!schemas) schemas = new jjv;
(function(){
	var my_meta_schema = {
	"id": "my_meta_schema", // название схемы
	"$schema": "http://json-schema.org/draft-04/schema#", // версия/схема этой схемы
	"description": "Core schema's meta-schema", // описание этой схемы
	"definitions": { // определения
		"schemaArray": { 
			"type": "array", // массив
			"minItems": 1, // содержащий по крайней мере 1 элемент
			"items": { "$ref": "#" } // каждый элемент - это схема (?)
		},
		"schemaList": {
			"type": "object", // объект
			"additionalProperties": { "$ref": "#" }, // каждое свойство которого - схема
			"default": {} // если отсутствует, можно считать, что присутствует и равен пустому объекту
		},
		"positiveInteger": {
			"type": "integer", // цело число
			"minimum": 0 // которое >=0
		},
		"positiveIntegerDefault0": {
			"allOf": [ { "$ref": "#/definitions/positiveInteger" }, { "default": 0 } ]
			// является positiveInteger, если отсутствует, можно считать, что присутствует и равен 0
		},
		"simpleTypes": { // здесь перечислены все примитивные типы JSON
			"enum": [ "null", "boolean", "integer", "number", "string", "array", "object" ]
			// должен быть равен одной из перечисленных строк
			// Напоминание: "number" включают "integer". 
		},
		"stringArray": {
			"type": "array", // массив
			"items": { "type": "string" }, // со строковыми элементами
			"minItems": 1, // содержащий по крайней мере 1 элемент
			"uniqueItems": true // все эелементы разные
		},
		//additions:
		"$data": { // для почти каждого ключевого слова можно вместо его значения предоставить ссылку/указатель на это значение
			"type": "object", // объект
			"required": [ "$data" ], // содержащий по крайней мере одно свойство "$data"
			"properties": {
				"$data": { "type": "string", "format": "relative-json-pointer" }
				// которое является строкой формата relative-json-pointer
			},
			"additionalProperties": true
		}
	},
	"type": "object", // JSON schema должна быть объектом
	"properties": { // и может иметь следующие свойства, которые называются keywords
	/* === общие === */
		"id": { // строка формата uri или identifier
			// идентификатор этой схемы, на который можно ссылаться как на JSON-reference или как на идентификатор
			/*	пример:
				{
					"id": "http://x.y.z/rootschema.json#",
					"schema1": {
						"id": "#foo"
					},
					"schema2": {
						"id": "otherschema.json",
						"nested": {
							"id": "#bar"
						},
						"alsonested": {
							"id": "t/inner.json#a"
						}
					},
					"schema3": {
						"id": "some://where.else/completely#"
					}
				}
				на эти схемы можно ссылаться следующим образом:

				# (document root)
					http://x.y.z/rootschema.json# 
				#/schema1
					http://x.y.z/rootschema.json#foo 
				#/schema2
					http://x.y.z/otherschema.json# 
				#/schema2/nested
					http://x.y.z/otherschema.json#bar 
				#/schema2/alsonested
					http://x.y.z/t/inner.json#a 
				#/schema3
					some://where.else/completely# 
			*/
			"type": "string",
			"anyOf": [	{"format": "uri"}, {"format": "identifier"} ]
		},
		"$schema": { // строка формата uri или identifier
			// версия схемы, ввиде ссылки на схему, описывающую эту схему
			// если в схеме используются другие ключевые слова, у этой схемы должна (SHOULD) быть не стандартная схема
			// по стандарту, версия схемы должна присутствовать в любой схеме
			"type": "string",
			"anyOf": [	{"format": "uri"}, {"format": "identifier"} ]
		},
		"title": { // как комментарий (короткий)
			"type": "string"
		},
		"description": { // как комментарий (развернутый)
			"type": "string"
		},
		"definitions": { "$ref": "#/definitions/schemaList" }, // стандартное место для размещения подсхем
	// если keyword не в состоянии определить валидность значения нек. типа, то оно считается валидным
	/* === для любых типов === */
		// пустая схема также как и отсутствующая схема не накладывает ограничений
		"allOf": { "$ref": "#/definitions/schemaArray" }, // значение удовлетворяет всем заданным схемам
		"anyOf": { "$ref": "#/definitions/schemaArray" }, // значение удовлетворяет любой из заданных схем
		"oneOf": { "$ref": "#/definitions/schemaArray" }, // значение удовлетворяет только одной из заданных схем
		"not": { "$ref": "#" }, // значение не удовлетворяет заданной схеме
		"enum": { "oneOf": [ // если указано, то значение должно быть одним из этого массива
			{
				"type": "array",
				"minItems": 1,
				"uniqueItems": true
			},
			{ "$ref": "#/definitions/$data" }//added
		]},
		/* алгоритм сравнения:
			both are nulls; or
			both are booleans, and have the same value; or
			both are strings, and have the same value; or
			both are numbers, and have the same mathematical value; or
			both are arrays, and:
				have the same number of items; and
				items at the same index are equal according to this definition; or
			both are objects, and:
				have the same set of property names; and
				values for a same property name are equal according to this definition.
		*/
		"type": { "anyOf": [
			{ "$ref": "#/definitions/simpleTypes" }, // значение имеет один заданный тип
			{
				"type": "array", // значение имеет один из заданных типов
				"items": { "$ref": "#/definitions/simpleTypes" },
				"minItems": 1,
				"uniqueItems": true
			}
		]},
		"format": { "oneOf": [
			{ "type": "string", "enum": [
				"relative-json-pointer", // /^\d*(\/.*)?$/
				"json-reference", // /^([_a-zA-Z][-_a-zA-Z0-9]*)?(#(\/.*)?)?$/
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
			]},
			{ "$ref":"#/definitions/$data" }
		]},
	/* === для целых чисел === */
		"multipleOf": { "oneOf": [ // число будет валидно, если оно делится на заданное число
			{ // число строго большее нуля
				"type": "number",
				"minimum": 0,
				"exclusiveMinimum": true
			},
			{ "$ref": "#/definitions/$data" }//added
		]},
		"maximum": { "oneOf":[ // число будет валидно, если оно не*строго меньше
			{ "type": "number" },
			{ "$ref": "#/definitions/$data" }//added
		]},
		"exclusiveMaximum": { "type": "boolean", "default": false },
		// если true - то строго
		// + зависимость "exclusiveMaximum": [ "maximum" ],
		"minimum": { "oneOf": [ // число будет валидно, если оно не*строго больше
			{ "type": "number" },
			{ "$ref": "#/definitions/$data" }//added
		]},
		"exclusiveMinimum": { "type": "boolean", "default": false },
		// если true - то строго
		// + зависимость "exclusiveMinimum": [ "minimum" ],
	/* === для строк === */
		"maxLength": { "oneOf": [
			{ "$ref": "#/definitions/positiveInteger" },
			{ "$ref": "#/definitions/$data" }//added
		]},
		"minLength": { "oneOf": [
			{ "$ref": "#/definitions/positiveIntegerDefault0" },
			{ "$ref": "#/definitions/$data" }//added
		]},
		"pattern": { "oneOf": [
			{ "type": "string", "format": "regex" },
			{ "$ref": "#/definitions/$data" }//added
		]},
	/* === для массивов === */
		"additionalItems": { "anyOf": [
				{ "type": "boolean" }, // true эквивалентно пустой схеме
				{ "$ref": "#" } // см. items
			],
			"default": {}
		},
		"items": { "anyOf": [
				{ "$ref": "#" }, // если это схема, то ВСЕ эементы должны удовлетворять этой схеме, независимо от additionalItems
				{ "$ref": "#/definitions/schemaArray" } // если это массив схем, то 
					// элементы с индексом, меньшим размера этого массива должны удовлетворять соотв. схеме
					// иначе они должны удовлетворять additionalItems
			],
			"default": {}
		},
		// если additionalItems == false && items - массив и в проверяемом массиве элементов больше чем в items - валидация провалена
		"maxItems": { "oneOf": [ // максимальное кол-во элементов в массиве
			{ "$ref": "#/definitions/positiveInteger" },
			{ "$ref": "#/definitions/$data" }//added
		]},
		"minItems": { "oneOf": [ // минимальное кол-во элементов в массиве
			{ "$ref": "#/definitions/positiveIntegerDefault0" },
			{ "$ref": "#/definitions/$data" }//added
		]},
		"uniqueItems": { "oneOf": [ // должны ли элементы массива быть уникальными
			{ "type": "boolean", "default": false },
			{ "$ref": "#/definitions/$data" }//added
		]},
	/* === для объектов === */
		"maxProperties": { "oneOf": [ // максимальное кол-во свойств в объекте
			{ "$ref": "#/definitions/positiveInteger" },
			{ "$ref": "#/definitions/$data" }//added
		]},
		"minProperties": { "oneOf": [ // минимальное кол-во свойств в объекте
			{ "$ref": "#/definitions/positiveIntegerDefault0" },
			{ "$ref": "#/definitions/$data" }//added
		]},
		"required": { "$ref": "#/definitions/stringArray" }, // список обязательно присутствующих свойств в объекте
		"additionalProperties": { "anyOf": [
				{ "type": "boolean" }, // true эквивалентно пустой схеме
				{ "$ref": "#" } // испоьзуется для свойства только если оно не подошло ни для properties ни для patternProperties
			],
			"default": {}
		},
		// если свойство подходит под properties и под несколько паттернов из patternProperties,
		// то оно должно удовлетворять всем этис схемам
		"properties": { "$ref": "#/definitions/schemaList" }, // точные названия свойств и схемы к ним
		"patternProperties": { "$ref": "#/definitions/schemaList" }, // паттерны для имен свойств и схемы к ним
		// если additionalProperties === false то, если из списка всех свойств удалить перечисленные в properties
		// а потом все, которые подпадают хоть под один regexp из patternProperties, и после этого что-то останется, 
		// то валидация провалена
		"uniquePatternProperties": { "$ref": "#/definitions/schemaList" },
		"dependencies": {
			"type": "object",
			"additionalProperties": { "anyOf": [
				{ "$ref": "#" }, // если объект имеет это свойство, то объект должен удовлетворять этой схеме
				{ "$ref": "#/definitions/stringArray" } // // если объект имеет это свойство, то объект должен 
					// иметь свойства, перечисленные в массиве
			]}
		},
		"default": {}, // если свойство отсутствует - его можно создать
	// === additions ===
		"$ref": { "type":"string", "format":"json-reference" }, // #todo сделать ввиде отдельной схемы, а потом объединить их третьей схемой
		// вместо описания схемы можно предоставить ссылку на схему при помощи $ref
		"readOnly": { "oneOf": [ // и зачем ???
			{ "type": "boolean" },
			{ "$ref":"#/definitions/$data" }
		]},
		"constant": { }, // есть же enum ???
		"isPropertyOf": { "oneOf": [ // вот это полезно, но только в js а не json
			{ "type": "string", "format": "relative-json-pointer" },
			{ "$ref":"#/definitions/$data" }
		]},
		"parseCoerce": { "type": "string" },
		"stringifyCoerce": { "type": "string" }
	},
	"additionalProperties": false, //modified
	// по стандарту схема может содержать другие свойства, они огнорируются, там например можно содержать другие подсхемы
	// каждый валидатор может добавлять свои ключевые слова, которые должны игнорироваться другими валидаторами
	"dependencies": {
		"exclusiveMaximum": [ "maximum" ],
		"exclusiveMinimum": [ "minimum" ],
		"properties": [ "additionalProperties" ], //modified
		"patternProperties": [ "additionalProperties" ], //modified
		"items": { "anyOf": [
			{
				"properties": {
					"items": { "type": "object" }
				},
				"additionalProperties": true
			},
			{
				"required": [ "items", "additionalItems" ],
				"properties": {
					"items": { "type": "array" }
				},
				"additionalProperties": true
			}
		]} //modified
	},
	"default": {}
};
	var res = schemas.addSchema('my_meta_schema',my_meta_schema).validate('my_meta_schema',my_meta_schema);
	if(res){
		console.dir(res);
		alert('мета-схема не валидна');
	}
})();
/*
#todo
	strictMinimum
	strictMaximum
	requredProperties
	oneOfPropSchemas
	allOfPropSchemas
	anyOfPropSchemas
*/