import os

import pandas as pd
from django.conf import settings
from django.db import transaction
from django.apps import apps
from django.http import JsonResponse
from datetime import datetime


def clean_text(value):
    """Utility function to clean text: lowercase, remove double spaces, and strip."""
    if isinstance(value, str):
        return ' '.join(value.lower().strip().split())
    return value


def split_and_clean(value):
    """Split values by '|' and clean each part."""
    if isinstance(value, str):
        return [clean_text(v) for v in value.split('|') if v.strip()]
    return []


def generate_short_name(name):
    """Generate short name using the first letter of each word."""
    if not name:
        return ""
    return ''.join(word[0].lower() for word in name.split())


def data_upload_view(request):
    if request.method == 'GET':
        # File path
        # excel_file_path = r'C:\Users\waltjos01\PycharmProjects\epe_v2.0\epe\media\consolidated_Excel_v2.0.xlsx'
        excel_file_path = os.path.join(settings.MEDIA_ROOT, 'consolidated_Excel_v2.0.xlsx')
        # Read the Excel file
        df = pd.read_excel(excel_file_path)

        # Process 'System' column
        system_model = apps.get_model('epe_app', 'system_Info')
        system_mapping = {}
        with transaction.atomic():
            for value in df['System'].dropna().unique():
                for cleaned_value in split_and_clean(value):
                    short_name = generate_short_name(cleaned_value)
                    obj, _ = system_model.objects.get_or_create(
                        system_name=cleaned_value,
                        defaults={'system_name_short': short_name}
                    )
                    system_mapping[cleaned_value] = obj.pk

        # Process 'Equipment' column
        equipment_model = apps.get_model('epe_app', 'equipmentInfo')
        with transaction.atomic():
            for value in df['Equipment'].dropna().unique():
                for cleaned_value in split_and_clean(value):
                    system_values = df.loc[df['Equipment'] == value, 'System'].dropna().unique()
                    for system_value in system_values:
                        for system_name in split_and_clean(system_value):
                            system_id = system_mapping.get(system_name)
                            short_name = generate_short_name(cleaned_value)
                            equipment_model.objects.get_or_create(
                                equipment_name=cleaned_value,
                                equipment_system_name_id=system_id,
                                defaults={'equipment_name_short': short_name}
                            )

        # Process 'Data Type' column
        datatype_model = apps.get_model('epe_app', 'datatype_Info')
        datatype_mapping = {}
        with transaction.atomic():
            for value in df['Data Type'].dropna().unique():
                for cleaned_value in split_and_clean(value):
                    obj, _ = datatype_model.objects.get_or_create(dt_name=cleaned_value)
                    datatype_mapping[cleaned_value] = obj.pk

        # Process 'Discipline Attribute Ownership' column
        owner_model = apps.get_model('epe_app', 'owner_info')
        with transaction.atomic():
            for value in df['Discipline Attribute Ownership'].dropna().unique():
                for cleaned_value in split_and_clean(value):
                    owner_model.objects.get_or_create(owner_name=cleaned_value)

        # Process 'Digital Data Source' column
        digital_source_model = apps.get_model('epe_app', 'digital_source_info')
        with transaction.atomic():
            for value in df['Digital Data Source'].dropna().unique():
                for cleaned_value in split_and_clean(value):
                    digital_source_model.objects.get_or_create(ds_name=cleaned_value)

        # Process 'Unit Type' column
        unit_type_model = apps.get_model('epe_app', 'unit_type_info')
        unit_type_mapping = {}
        with transaction.atomic():
            for value in df['Unit Type'].dropna().unique():
                for cleaned_value in split_and_clean(value):
                    obj, _ = unit_type_model.objects.get_or_create(ut_name=cleaned_value)
                    unit_type_mapping[cleaned_value] = obj.pk

        # Process 'UOM' column
        uom_model = apps.get_model('epe_app', 'uom_info')
        with transaction.atomic():
            for value in df['UOM'].dropna().unique():
                for cleaned_value in split_and_clean(value):
                    unit_type_name = clean_text(df.loc[df['UOM'] == value, 'Unit Type'].iloc[0])
                    unit_type_id = unit_type_mapping.get(unit_type_name)
                    uom_model.objects.get_or_create(
                        uom_symbol=cleaned_value,
                        defaults={'uom_unit_type_id': unit_type_id}
                    )

        # Process 'DICTIONARY Parameter' column
        dictionary_model = apps.get_model('epe_app', 'dictionary_Info')
        pd_library_instance = dictionary_model.objects.get(pk=1)
        status_model = apps.get_model('epe_app', 'status_Info')
        pd_status_instance = status_model.objects.get(pk=1)
        user_model = apps.get_model('epe_app', 'MyUser')
        pd_updated_by_instance = user_model.objects.get(pk=1)
        parameter_definition_model = apps.get_model('epe_app', 'prameter_definition_info')
        with transaction.atomic():
            for value in df['DICTIONARY Parameter'].dropna().unique():
                for cleaned_value in split_and_clean(value):
                    unit_type_name = clean_text(df.loc[df['DICTIONARY Parameter'] == value, 'Unit Type'].iloc[0])
                    unit_type_id = unit_type_mapping.get(unit_type_name)
                    # Skip the record if unit_type_id is None
                    if unit_type_id is None:
                        continue

                    data_type_name = clean_text(df.loc[df['DICTIONARY Parameter'] == value, 'Data Type'].iloc[0])
                    data_type_id = datatype_mapping.get(data_type_name)
                    description = clean_text(df.loc[df['DICTIONARY Parameter'] == value, 'PARAMETER Description'].iloc[0])
                    parameter_definition_model.objects.get_or_create(
                        pd_name=cleaned_value,
                        defaults={
                            'pd_unit_type_id': unit_type_id,
                            'pd_library': pd_library_instance,
                            'pd_status': pd_status_instance,
                            'pd_id': f"PD_{1000000 + parameter_definition_model.objects.count() + 1}",
                            'pd_description': description,
                            'pd_updated_at': datetime.now(),
                            'pd_updated_by': pd_updated_by_instance,
                            'pd_datatype_id': data_type_id
                        }
                    )

        # Process 'List Of Discrete Values' column
        parameter_definition_model = apps.get_model('epe_app', 'prameter_definition_info')
        parameter_definition_lov_model = apps.get_model('epe_app', 'parameter_definition_lov_info')

        # Process 'List Of Discrete Values' column
        with transaction.atomic():
            for index, row in df.dropna(subset=['List Of Discrete Values', 'DICTIONARY Parameter']).iterrows():
                # Get the corresponding parameter definition
                pd_name = clean_text(row['DICTIONARY Parameter'])
                parameter_definition = parameter_definition_model.objects.filter(pd_name=pd_name).first()

                if not parameter_definition:
                    continue  # Skip if no matching parameter definition is found

                # Ensure 'List Of Discrete Values' is processed as a string
                if isinstance(row['List Of Discrete Values'], (str, int)):
                    lov_values = [clean_text(value) for value in str(row['List Of Discrete Values']).split('|')]
                else:
                    lov_values = []  # Handle other non-string/non-integer values gracefully
                for lov_value in lov_values:
                    # Ensure the value is unique for the parameter definition
                    if not parameter_definition_lov_model.objects.filter(
                            pdl_parameter_definition=parameter_definition, pdl_lov=lov_value
                    ).exists():
                        parameter_definition_lov_model.objects.create(
                            pdl_parameter_definition=parameter_definition,
                            pdl_lov=lov_value
                        )

        # Process 'Parameter instance' column
        parameter_info_model = apps.get_model('epe_app', 'prameter_info')
        with transaction.atomic():
            for index, row in df.dropna(subset=['Parameter instance']).iterrows():
                # Clean and extract values
                parameter_instance = clean_text(row['Parameter instance'])
                dictionary_parameter = clean_text(row['DICTIONARY Parameter'])
                doct_as_is_parameter = clean_text(row['DOCT AS IS PARAMETER NOMENCLATURE'])
                uom = clean_text(row['UOM'])
                system = clean_text(row['System'])
                unit_type = clean_text(row['Unit Type'])
                equipment = clean_text(row['Equipment'])
                parameter_prefix = clean_text(row['Parameter Definition Sub Class'])

                # Define a mapping of model fields to their corresponding instance variables
                field_mapping = {
                    'p_definition': ('prameter_definition_info', dictionary_parameter, 'pd_name'),
                    'p_uom': ('uom_info', uom, 'uom_symbol'),
                    'p_system': ('system_Info', system, 'system_name'),
                    'p_unit_type': ('unit_type_info', unit_type, 'ut_name'),
                    'p_equipment_name': ('equipmentInfo', equipment, 'equipment_name'),
                }

                # Dynamically fetch instances
                defaults = {
                    'p_id': f"P_{1000000+parameter_info_model.objects.count() + 1}",
                    'p_name_as_is': doct_as_is_parameter,
                    'p_parameter_name_combo': parameter_instance,
                    'p_status': pd_status_instance,
                    'p_updated_at': datetime.now(),
                    'p_updated_by': pd_updated_by_instance,
                    'p_parameter_prefix': parameter_prefix,
                }
                # print('parameter_instance:', parameter_instance, 'Length:', len(parameter_instance))

                # Fetch short names for system and equipment
                system_instance = apps.get_model('epe_app', 'system_Info').objects.filter(system_name=system).first()
                if system_instance:
                    defaults['p_system_short'] = system_instance.system_name_short

                equipment_instance = apps.get_model('epe_app', 'equipmentInfo').objects.filter(equipment_name=equipment).first()
                if equipment_instance:
                    defaults['p_equipment_short'] = equipment_instance.equipment_name_short

                for field, (model_name, value, lookup_field) in field_mapping.items():
                    # Dynamically get the model
                    model = apps.get_model('epe_app', model_name)

                    # Fetch the instance based on the lookup field and value
                    instance = model.objects.filter(**{lookup_field: value}).first()

                    if instance:
                        # Assign the instance to the defaults dictionary
                        defaults[field] = instance
                    else:
                        # Log missing mapping and break the loop
                        print(f"Missing mapping for {field}: {value}")
                        break
                else:
                    # Create or update the record if all mappings are valid
                    parameter_info_model.objects.update_or_create(
                        p_parameter_name_combo=parameter_instance,
                        defaults=defaults
                    )

        # Process 'Digital Data Source' column for prameter_info table
        parameter_info_model = apps.get_model('epe_app', 'prameter_info')
        digital_source_model = apps.get_model('epe_app', 'digital_source_info')

        with transaction.atomic():
            for index, row in df.dropna(subset=['Digital Data Source']).iterrows():
                # Get the parameter_info instance
                parameter_instance = clean_text(row['Parameter instance'])
                parameter_info = parameter_info_model.objects.filter(p_parameter_name_combo=parameter_instance).first()

                if not parameter_info:
                    print(f"Missing parameter_info for: {parameter_instance}")
                    continue

                # Split and clean digital data source values
                digital_sources = split_and_clean(row['Digital Data Source'])

                for digital_source in digital_sources:
                    # Get the digital_source_info instance
                    digital_source_info = digital_source_model.objects.filter(ds_name=digital_source).first()

                    if not digital_source_info:
                        print(f"Missing digital_source_info for: {digital_source}")
                        continue

                    # Add the digital_source_info instance to the ManyToManyField
                    parameter_info.p_digital_source.add(digital_source_info)

        # Process 'Discipline Attribute Ownership' column for prameter_info table
        parameter_info_model = apps.get_model('epe_app', 'prameter_info')
        owner_info_model = apps.get_model('epe_app', 'owner_info')

        with transaction.atomic():
            # Extract and clean unique values from 'Discipline Attribute Ownership'
            unique_owners = set()
            for value in df['Discipline Attribute Ownership'].dropna():
                # Split by pipe separator and clean each value
                owners = [clean_text(owner) for owner in value.split('|') if owner.strip()]
                unique_owners.update(owners)

            # Insert unique cleaned values into the 'owner_info' table
            for owner in unique_owners:
                owner_info_model.objects.get_or_create(owner_name=owner)

        return JsonResponse({'success': True, 'message': 'Data uploaded successfully.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})