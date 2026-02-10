/*
 * StudyAI - MV (Minimum Viable) - Ultra Premium Edition
 * Modern AI Chat Application with SVG Graphics & Advanced Features
 * Rheehose (Rhee Creative) 2008-2026
 * Licensed under Apache-2.0
 */

#include <gtk/gtk.h>
#include <librsvg/rsvg.h>
#include <curl/curl.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <pthread.h>
#include "cJSON.h"

// Random greeting phrases for start screen
const char *greetings[] = {
    "How are you?",
    "What's on your mind?",
    "Ready to learn something new?",
    "Ask me anything!",
    "Let's explore together.",
    "What would you like to know?",
    "Curious about something?",
    "How can I help you today?",
    "Let's get started!",
    "What are you studying?",
    "Need help with homework?",
    "Let's solve a problem!",
    "What's your question?",
    "Think. Ask. Learn.",
    "Knowledge awaits you.",
    "Let's dive in!",
    "What brings you here?",
    "Ready when you are.",
    "Let's figure it out together.",
    "Got a tough question?",
    "I'm here to help.",
    "Let's make today productive.",
    "What topic interests you?",
    "Fire away!",
    "Challenge me with a question.",
    "Learning never stops.",
    "Stay curious, stay sharp.",
    "One question at a time.",
    "Your study buddy is ready.",
    "Let's crack this together.",
    "No question is too small.",
    "Explore. Discover. Grow.",
    "What shall we learn today?",
    "Tell me what you need.",
    "Stuck on something?",
    "Let me help you out.",
    "Wisdom starts with a question.",
    "Every expert was once a beginner.",
    "Keep asking, keep growing.",
    "Your journey starts here.",
    "Think big, ask bigger.",
    "Let's build understanding.",
    "Dare to be curious.",
    "Questions are the answer.",
    "Unlock your potential.",
    "Let's make progress.",
    "What's the next challenge?",
    "I'm all ears.",
    "Bring it on!",
    "The world is your classroom."
};
#define NUM_GREETINGS 50

// API Configuration
#define MISTRAL_API_KEY "OBfwuYKEEUFvjh5bLt18XOcVIpTYFHVQ"
#define MISTRAL_API_URL "https://api.mistral.ai/v1/chat/completions"
#define MODEL_NAME "mistral-small-latest"


// UI Widgets
GtkWidget *main_window;
GtkWidget *stack;
GtkWidget *chat_list_box;
GtkWidget *prompt_entry;
GtkWidget *scrolled_window;
GtkWidget *current_bot_label = NULL;
GString *current_bot_text = NULL;

int is_dark_mode = 0;
volatile int is_streaming = 0;

// Conversation history
#define MAX_MESSAGES 100
struct Message {
    char *role;
    char *content;
};
struct Message conversation_history[MAX_MESSAGES];
int message_count = 0;
int total_tokens = 0;
const int MAX_TOKENS = 32000;  // Mistral Small context limit

GtkWidget *context_label = NULL;
GtkWidget *streaming_dot_label = NULL;
guint dot_timer_id = 0;
int dot_visible = 1;

struct ThreadData {
    char *user_input;
};

// --- File Helper Functions ---

char* load_file_to_string(const char *filepath) {
    FILE *file = fopen(filepath, "r");
    if (!file) {
        g_warning("Failed to open file: %s", filepath);
        return NULL;
    }
    
    fseek(file, 0, SEEK_END);
    long length = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    char *content = malloc(length + 1);
    if (content) {
        fread(content, 1, length, file);
        content[length] = '\0';
    }
    
    fclose(file);
    return content;
}

// --- SVG Helper Functions ---

GdkPixbuf* svg_to_pixbuf(const char *svg_data, int width, int height) {
    GError *error = NULL;
    RsvgHandle *handle = rsvg_handle_new_from_data((const guint8*)svg_data, strlen(svg_data), &error);
    if (!handle) {
        if (error) g_error_free(error);
        return NULL;
    }
    
    GdkPixbuf *pixbuf = rsvg_handle_get_pixbuf_sub(handle, NULL);
    g_object_unref(handle);
    
    if (pixbuf && (width != -1 || height != -1)) {
        GdkPixbuf *scaled = gdk_pixbuf_scale_simple(pixbuf, width, height, GDK_INTERP_BILINEAR);
        g_object_unref(pixbuf);
        return scaled;
    }
    
    return pixbuf;
}

// --- Enhanced Markdown Parser with Heading Support ---

char* markdown_to_pango(const char *text) {
    GString *out = g_string_new("");
    int len = strlen(text);
    int in_bold = 0, in_italic = 0, in_code = 0;
    int i = 0;

    while (i < len) {
        // Handle Code Block (```)
        if (i + 2 < len && text[i] == '`' && text[i+1] == '`' && text[i+2] == '`') {
            // Find end of code block
            int start = i + 3;
            // Skip language identifier if present
            while (start < len && text[start] != '\n') start++;
            if (start < len) start++; // Skip newline
            
            int end = start;
            while (end + 2 < len) {
                if (text[end] == '`' && text[end+1] == '`' && text[end+2] == '`') {
                    break;
                }
                end++;
            }
            
            if (end + 2 < len) {
                // Render code block with light gray background (grayscale)
                g_string_append(out, "<span background='#f5f5f5' foreground='#333333'><tt>");
                for (int j = start; j < end; j++) {
                    if (text[j] == '<') g_string_append(out, "&lt;");
                    else if (text[j] == '&') g_string_append(out, "&amp;");
                    else g_string_append_c(out, text[j]);
                }
                g_string_append(out, "</tt></span>\n");
                i = end + 3;
                continue;
            }
        }
        
        // Handle Bullet Lists (- item)
        if (i == 0 || text[i-1] == '\n') {
            if (text[i] == '-' && i + 1 < len && text[i+1] == ' ') {
                g_string_append(out, "  • ");
                i += 2;
                continue;
            }
        }

        // Handle Heading (###)
        if (i == 0 || text[i-1] == '\n') {
            if (i + 2 < len && text[i] == '#' && text[i+1] == '#' && text[i+2] == '#' && text[i+3] == ' ') {
                // Find end of line
                int end = i + 4;
                while (end < len && text[end] != '\n') end++;
                
                g_string_append(out, "<span size='large' weight='bold'>");
                for (int j = i + 4; j < end; j++) {
                    if (text[j] == '<') g_string_append(out, "&lt;");
                    else if (text[j] == '&') g_string_append(out, "&amp;");
                    else g_string_append_c(out, text[j]);
                }
                g_string_append(out, "</span>\n");
                i = end + 1;
                continue;
            }
        }

        // Handle Inline Code (backtick)
        if (text[i] == '`') {
            if (in_code) {
                g_string_append(out, "</tt></span>");
                in_code = 0;
            } else {
                g_string_append(out, "<span background='#e8e8e8' foreground='#333'><tt>");
                in_code = 1;
            }
            i++;
            continue;
        }
        
        if (in_code) {
            if (text[i] == '<') g_string_append(out, "&lt;");
            else if (text[i] == '&') g_string_append(out, "&amp;");
            else g_string_append_c(out, text[i]);
            i++;
            continue;
        }

        // Handle Bold (**)
        if (i + 1 < len && text[i] == '*' && text[i+1] == '*') {
            in_bold = !in_bold;
            g_string_append(out, in_bold ? "<b>" : "</b>");
            i += 2;
            continue;
        }

        // Handle Italic (*)
        if (text[i] == '*') {
            in_italic = !in_italic;
            g_string_append(out, in_italic ? "<i>" : "</i>");
            i++;
            continue;
        }

        // Escape XML/Pango special chars
        if (text[i] == '<') g_string_append(out, "&lt;");
        else if (text[i] == '>') g_string_append(out, "&gt;");
        else if (text[i] == '&') g_string_append(out, "&amp;");
        else g_string_append_c(out, text[i]);
        i++;
    }
    
    if (in_code) g_string_append(out, "</tt></span>");
    if (in_bold) g_string_append(out, "</b>");
    if (in_italic) g_string_append(out, "</i>");

    return g_string_free(out, FALSE);
}

// --- Streaming Dot Indicator ---

gboolean blink_dot(gpointer user_data) {
    if (!is_streaming || !streaming_dot_label) return FALSE;
    dot_visible = !dot_visible;
    gtk_label_set_text(GTK_LABEL(streaming_dot_label), dot_visible ? "●" : " ");
    return TRUE;  // Keep timer going
}

// --- Auto-scroll Helper ---

gboolean scroll_to_bottom(gpointer user_data) {
    if (scrolled_window) {
        GtkAdjustment *adj = gtk_scrolled_window_get_vadjustment(GTK_SCROLLED_WINDOW(scrolled_window));
        gtk_adjustment_set_value(adj, gtk_adjustment_get_upper(adj) - gtk_adjustment_get_page_size(adj));
    }
    return FALSE;
}

// --- Streaming Callbacks ---

gboolean update_bot_message(gpointer user_data) {
    char *chunk = (char *)user_data;
    if (current_bot_text) {
        g_string_append(current_bot_text, chunk);
        if (current_bot_label) {
            char *markup = markdown_to_pango(current_bot_text->str);
            gtk_label_set_markup(GTK_LABEL(current_bot_label), markup);
            g_free(markup);
        }
        // Update streaming dot position - append after the label
        if (streaming_dot_label) {
            gtk_widget_show(streaming_dot_label);
        }
    }
    free(chunk);
    // Auto-scroll to bottom during streaming
    g_idle_add(scroll_to_bottom, NULL);
    return FALSE;
}

size_t StreamCallback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    char *data = malloc(realsize + 1);
    memcpy(data, contents, realsize);
    data[realsize] = 0;

    char *line = strtok(data, "\n");
    while (line != NULL) {
        if (strncmp(line, "data: ", 6) == 0) {
            const char *json_str = line + 6;
            if (strcmp(json_str, "[DONE]") == 0) break;
            
            cJSON *json = cJSON_Parse(json_str);
            if (json) {
                cJSON *choices = cJSON_GetObjectItemCaseSensitive(json, "choices");
                if (cJSON_IsArray(choices)) {
                    cJSON *choice = cJSON_GetArrayItem(choices, 0);
                    cJSON *delta = cJSON_GetObjectItemCaseSensitive(choice, "delta");
                    if (delta) {
                        cJSON *content = cJSON_GetObjectItemCaseSensitive(delta, "content");
                        if (cJSON_IsString(content)) {
                            g_idle_add(update_bot_message, strdup(content->valuestring));
                        }
                    }
                }
                cJSON_Delete(json);
            }
        }
        line = strtok(NULL, "\n");
    }

    free(data);
    return realsize;
}

// --- UI Components ---

// Create StudyAI text avatar
GtkWidget* create_text_avatar() {
    GtkWidget *avatar_label = gtk_label_new(NULL);
    gtk_label_set_markup(GTK_LABEL(avatar_label), "<b>Study\nAI</b>");
    gtk_label_set_justify(GTK_LABEL(avatar_label), GTK_JUSTIFY_CENTER);
    gtk_widget_set_size_request(avatar_label, 50, 50);
    gtk_widget_set_valign(avatar_label, GTK_ALIGN_START);  // Pin to top
    
    // Apply CSS class based on theme
    GtkStyleContext *context = gtk_widget_get_style_context(avatar_label);
    gtk_style_context_add_class(context, "avatar-text");
    
    return avatar_label;
}

// Copy button callback
void on_copy_clicked(GtkWidget *widget, gpointer user_data) {
    const char *text = (const char *)user_data;
    GtkClipboard *clipboard = gtk_clipboard_get(GDK_SELECTION_CLIPBOARD);
    gtk_clipboard_set_text(clipboard, text, -1);
}

// Reply button callback
void on_reply_clicked(GtkWidget *widget, gpointer user_data) {
    const char *text = (const char *)user_data;
    gtk_entry_set_text(GTK_ENTRY(prompt_entry), text);
    gtk_widget_grab_focus(prompt_entry);
    gtk_editable_set_position(GTK_EDITABLE(prompt_entry), -1);
}

GtkWidget* add_message_bubble(const char *text, int is_user) {
    GtkWidget *row_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 12);
    gtk_widget_set_margin_top(row_box, 8);
    gtk_widget_set_margin_bottom(row_box, 8);
    
    // Bot gets text avatar, user gets no icon
    GtkWidget *avatar = NULL;
    if (!is_user) {
        avatar = create_text_avatar();
    }
    
    // Content box with label and buttons
    GtkWidget *content_vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 6);
    
    GtkWidget *bubble_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 0);
    GtkWidget *label = gtk_label_new(text);
    gtk_label_set_line_wrap(GTK_LABEL(label), TRUE);
    gtk_label_set_max_width_chars(GTK_LABEL(label), 85);  // Increased from 50 to 85
    gtk_label_set_xalign(GTK_LABEL(label), 0.0);
    gtk_label_set_selectable(GTK_LABEL(label), TRUE);
    
    if (text && strlen(text) > 0) {
       char *markup = markdown_to_pango(text);
       gtk_label_set_markup(GTK_LABEL(label), markup);
       g_free(markup);
    }

    gtk_container_add(GTK_CONTAINER(bubble_box), label);
    gtk_widget_set_margin_top(bubble_box, 12);
    gtk_widget_set_margin_bottom(bubble_box, 12);
    gtk_widget_set_margin_start(bubble_box, 16);
    gtk_widget_set_margin_end(bubble_box, 16);
    
    GtkStyleContext *context = gtk_widget_get_style_context(bubble_box);
    gtk_style_context_add_class(context, "message-bubble");
    gtk_style_context_add_class(context, is_user ? "user-bubble" : "bot-bubble");
    
    gtk_box_pack_start(GTK_BOX(content_vbox), bubble_box, TRUE, TRUE, 0);
    
    // Add copy/reply buttons only for bot messages
    if (!is_user && text && strlen(text) > 0) {
        GtkWidget *button_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
        
        GtkWidget *copy_btn = gtk_button_new_with_label("📋 Copy");
        g_signal_connect(copy_btn, "clicked", G_CALLBACK(on_copy_clicked), g_strdup(text));
        gtk_style_context_add_class(gtk_widget_get_style_context(copy_btn), "action-btn");
        
        GtkWidget *reply_btn = gtk_button_new_with_label("↩ Reply");
        g_signal_connect(reply_btn, "clicked", G_CALLBACK(on_reply_clicked), g_strdup(text));
        gtk_style_context_add_class(gtk_widget_get_style_context(reply_btn), "action-btn");
        
        gtk_box_pack_start(GTK_BOX(button_box), copy_btn, FALSE, FALSE, 0);
        gtk_box_pack_start(GTK_BOX(button_box), reply_btn, FALSE, FALSE, 0);
        
        gtk_box_pack_start(GTK_BOX(content_vbox), button_box, FALSE, FALSE, 0);
    }
    
    if (is_user) {
        if (avatar) gtk_box_pack_end(GTK_BOX(row_box), avatar, FALSE, FALSE, 0);
        gtk_box_pack_end(GTK_BOX(row_box), content_vbox, FALSE, FALSE, 0);
        gtk_widget_set_halign(row_box, GTK_ALIGN_END);
    } else {
        if (avatar) {
            gtk_box_pack_start(GTK_BOX(row_box), avatar, FALSE, FALSE, 0);
            gtk_widget_set_valign(avatar, GTK_ALIGN_START);  // Ensure top alignment
        }
        gtk_box_pack_start(GTK_BOX(row_box), content_vbox, FALSE, FALSE, 0);
        gtk_widget_set_halign(row_box, GTK_ALIGN_START);
    }
    
    gtk_widget_set_margin_start(row_box, 20);
    gtk_widget_set_margin_end(row_box, 20);
    
    gtk_list_box_insert(GTK_LIST_BOX(chat_list_box), row_box, -1);
    gtk_widget_show_all(row_box);
    
    // Auto-scroll to bottom when new message added
    g_idle_add(scroll_to_bottom, NULL);
    
    return label;
}

gboolean completion_finished(gpointer data) {
    is_streaming = 0;
    gtk_widget_set_sensitive(prompt_entry, TRUE);
    
    // Stop blinking dot
    if (dot_timer_id) {
        g_source_remove(dot_timer_id);
        dot_timer_id = 0;
    }
    if (streaming_dot_label) {
        gtk_widget_hide(streaming_dot_label);
    }
    
    // Add bot response to history
    if (current_bot_text && message_count < MAX_MESSAGES) {
        conversation_history[message_count].role = strdup("assistant");
        conversation_history[message_count].content = strdup(current_bot_text->str);
        message_count++;
        
        // Estimate tokens (rough: 4 chars per token)
        total_tokens += strlen(current_bot_text->str) / 4;
        
        // Update context display
        if (context_label) {
            int percentage = (total_tokens * 100) / MAX_TOKENS;
            char status[256];
            snprintf(status, sizeof(status), "Context: %d/%d tokens (%d%%)", 
                     total_tokens, MAX_TOKENS, percentage);
            gtk_label_set_text(GTK_LABEL(context_label), status);
        }
    }
    
    return FALSE;
}

void *api_thread_func(void *data) {
    struct ThreadData *tdata = (struct ThreadData *)data;
    CURL *curl = curl_easy_init();
    
    if(curl) {
        cJSON *root = cJSON_CreateObject();
        cJSON_AddStringToObject(root, "model", MODEL_NAME);
        cJSON_AddBoolToObject(root, "stream", cJSON_True);
        cJSON *messages = cJSON_CreateArray();
        
        // Add system message
        cJSON *system_msg = cJSON_CreateObject();
        cJSON_AddStringToObject(system_msg, "role", "system");
        cJSON_AddStringToObject(system_msg, "content", 
            "You are StudyAI, a smart study assistant. "
            "Adapt your response length to the question: "
            "- Simple/greeting questions: 1-2 sentences. "
            "- Factual questions: 1 short paragraph. "
            "- Explanations/how-to: concise but thorough, use bullet points. "
            "- Code requests: provide clean, commented code with brief explanation. "
            "- Deep analysis: comprehensive but well-structured with headers. "
            "Use markdown: ### headers, **bold**, `code`, ```code blocks```, lists. "
            "Never pad responses unnecessarily. Be precise and useful.");
        cJSON_AddItemToArray(messages, system_msg);
        
        // Add conversation history
        for (int i = 0; i < message_count; i++) {
            cJSON *hist_msg = cJSON_CreateObject();
            cJSON_AddStringToObject(hist_msg, "role", conversation_history[i].role);
            cJSON_AddStringToObject(hist_msg, "content", conversation_history[i].content);
            cJSON_AddItemToArray(messages, hist_msg);
        }
        
        // Add current user message
        cJSON *user_msg = cJSON_CreateObject();
        cJSON_AddStringToObject(user_msg, "role", "user");
        cJSON_AddStringToObject(user_msg, "content", tdata->user_input);
        cJSON_AddItemToArray(messages, user_msg);
        
        cJSON_AddItemToObject(root, "messages", messages);
        
        char *json_str = cJSON_PrintUnformatted(root);
        
        struct curl_slist *headers = NULL;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        char auth_header[256];
        snprintf(auth_header, sizeof(auth_header), "Authorization: Bearer %s", MISTRAL_API_KEY);
        headers = curl_slist_append(headers, auth_header);

        curl_easy_setopt(curl, CURLOPT_URL, MISTRAL_API_URL);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_str);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, StreamCallback);
        
        curl_easy_perform(curl);
        
        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
        cJSON_Delete(root);
        free(json_str);
    }
    
    free(tdata->user_input);
    free(tdata);
    g_idle_add(completion_finished, NULL);
    pthread_exit(NULL);
}

void on_send_clicked(GtkWidget *widget, gpointer data) {
    if (is_streaming) return;

    const char *text = gtk_entry_get_text(GTK_ENTRY(prompt_entry));
    if (strlen(text) > 0) {
        gtk_stack_set_transition_type(GTK_STACK(stack), GTK_STACK_TRANSITION_TYPE_SLIDE_LEFT);
        gtk_stack_set_transition_duration(GTK_STACK(stack), 300);
        gtk_stack_set_visible_child_name(GTK_STACK(stack), "chat_view");
        
        add_message_bubble(text, 1);
        
        // Add user message to history
        if (message_count < MAX_MESSAGES) {
            conversation_history[message_count].role = strdup("user");
            conversation_history[message_count].content = strdup(text);
            message_count++;
            total_tokens += strlen(text) / 4;  // Rough estimate
        }
        
        if (current_bot_text) g_string_free(current_bot_text, TRUE);
        current_bot_text = g_string_new("");
        current_bot_label = add_message_bubble("", 0);
        
        // Create streaming dot indicator in the bot bubble's parent
        if (streaming_dot_label) {
            gtk_widget_destroy(streaming_dot_label);
        }
        streaming_dot_label = gtk_label_new("●");
        gtk_widget_set_halign(streaming_dot_label, GTK_ALIGN_START);
        gtk_widget_set_margin_start(streaming_dot_label, 82);
        gtk_list_box_insert(GTK_LIST_BOX(chat_list_box), streaming_dot_label, -1);
        gtk_widget_show(streaming_dot_label);
        
        // Start blinking timer (300ms interval)
        dot_visible = 1;
        dot_timer_id = g_timeout_add(300, blink_dot, NULL);
        
        is_streaming = 1;
        gtk_widget_set_sensitive(prompt_entry, FALSE);
        
        struct ThreadData *tdata = malloc(sizeof(struct ThreadData));
        tdata->user_input = strdup(text);
        
        pthread_t thread_id;
        pthread_create(&thread_id, NULL, api_thread_func, (void *)tdata);
        pthread_detach(thread_id);
        
        gtk_entry_set_text(GTK_ENTRY(prompt_entry), "");
    }
}

void set_theme(int dark) {
    GtkCssProvider *provider = gtk_css_provider_new();
    const char *css;
    
    if (dark) {
        css = 
        "window { background: linear-gradient(135deg, #1a1a1a, #2d2d2d, #1f1f1f); color: #fff; }"
        "list { background: transparent; }"
        ".message-bubble { padding: 14px 18px; border-radius: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); transition: all 0.2s; font-size: 15px; }"
        ".message-bubble:hover { box-shadow: 0 6px 16px rgba(0,0,0,0.5); }"
        ".user-bubble { background: linear-gradient(135deg, #4a4a4a, #5a5a5a); color: white; }"
        ".bot-bubble { background: rgba(255,255,255,0.08); color: #e0e0e0; border: 1px solid rgba(255,255,255,0.1); }"
        "entry { background: rgba(255,255,255,0.1); color: white; border-radius: 24px; border: 1px solid rgba(255,255,255,0.2); padding: 12px 20px; font-size: 14px; }"
        "entry:focus { border-color: #666; box-shadow: 0 0 0 3px rgba(102,102,102,0.3); }"
        "button.send-btn { background: linear-gradient(135deg, #4a4a4a, #5a5a5a); color: white; border-radius: 24px; font-weight: 600; border: none; padding: 12px 28px; transition: all 0.3s; }"
        "button.send-btn:hover { box-shadow: 0 8px 24px rgba(74,74,74,0.4); }"
        "button.action-btn { background: rgba(102,102,102,0.15); color: #999; border-radius: 12px; border: 1px solid rgba(102,102,102,0.3); padding: 6px 12px; font-size: 12px; transition: all 0.2s; }"
        "button.action-btn:hover { background: rgba(102,102,102,0.25); }"
        ".avatar-text { background: linear-gradient(135deg, #4a4a4a, #5a5a5a); color: white; border-radius: 8px; padding: 8px; font-size: 11px; font-weight: bold; }"
        "label.title { font-size: 42px; font-weight: 700; color: white; text-shadow: 0 4px 20px rgba(102,102,102,0.5); }"
        "label.subtitle { font-size: 16px; color: rgba(255,255,255,0.7); font-weight: 300; letter-spacing: 0.5px; }"
        "label.context-info { font-size: 12px; color: rgba(255,255,255,0.6); }";
    } else {
        css = 
        "window { background: linear-gradient(135deg, #ffffff, #f5f5f5, #fafafa); color: #333; }"
        "list { background: transparent; }"
        ".message-bubble { padding: 14px 18px; border-radius: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: all 0.2s; font-size: 15px; }"
        ".message-bubble:hover { box-shadow: 0 6px 16px rgba(0,0,0,0.12); }"
        ".user-bubble { background: linear-gradient(135deg, #6a6a6a, #7a7a7a); color: white; }"
        ".bot-bubble { background: #ffffff; color: #333; border: 1px solid rgba(0,0,0,0.1); }"
        "entry { background: #ffffff; color: #333; border-radius: 24px; border: 1px solid rgba(0,0,0,0.15); padding: 12px 20px; font-size: 14px; }"
        "entry:focus { border-color: #888; box-shadow: 0 0 0 3px rgba(136,136,136,0.15); }"
        "button.send-btn { background: linear-gradient(135deg, #5a5a5a, #6a6a6a); color: white; border-radius: 24px; font-weight: 600; border: none; padding: 12px 28px; transition: all 0.3s; }"
        "button.send-btn:hover { box-shadow: 0 6px 20px rgba(90,90,90,0.25); }"
        "button.action-btn { background: rgba(102,102,102,0.08); color: #555; border-radius: 12px; border: 1px solid rgba(0,0,0,0.15); padding: 6px 12px; font-size: 12px; transition: all 0.2s; }"
        "button.action-btn:hover { background: rgba(102,102,102,0.15); color: #333; }"
        ".avatar-text { background: linear-gradient(135deg, #5a5a5a, #6a6a6a); color: white; border-radius: 8px; padding: 8px; font-size: 11px; font-weight: bold; }"
        "label.title { font-size: 42px; font-weight: 700; color: #444; text-shadow: 0 2px 10px rgba(68,68,68,0.15); }"
        "label.subtitle { font-size: 16px; color: rgba(68,68,68,0.65); font-weight: 300; letter-spacing: 0.5px; }"
        "label.context-info { font-size: 12px; color: rgba(0,0,0,0.5); }";
    }
    
    gtk_css_provider_load_from_data(provider, css, -1, NULL);
    GdkScreen *screen = gdk_screen_get_default();
    gtk_style_context_add_provider_for_screen(screen, GTK_STYLE_PROVIDER(provider), GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);
    g_object_unref(provider);
}

void on_toggle_theme(GtkWidget *widget, gpointer data) {
    is_dark_mode = !is_dark_mode;
    set_theme(is_dark_mode);
    gtk_button_set_label(GTK_BUTTON(widget), is_dark_mode ? "☀" : "🌙");
}

gboolean pulse_logo(gpointer user_data) {
    static double scale = 1.0;
    static int direction = 1;
    
    GtkWidget *logo = (GtkWidget *)user_data;
    
    scale += direction * 0.02;
    if (scale > 1.1) direction = -1;
    if (scale < 0.95) direction = 1;
    
    gtk_widget_queue_draw(logo);
    
    return TRUE;
}

int main(int argc, char *argv[]) {
    srand(time(NULL));
    gtk_init(&argc, &argv);

    main_window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(main_window), "StudyAI - Ultra Premium");
    gtk_window_set_default_size(GTK_WINDOW(main_window), 480, 720);
    g_signal_connect(main_window, "destroy", G_CALLBACK(gtk_main_quit), NULL);

    GtkWidget *main_vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 0);
    gtk_container_add(GTK_CONTAINER(main_window), main_vbox);

    GtkWidget *header = gtk_header_bar_new();
    gtk_header_bar_set_show_close_button(GTK_HEADER_BAR(header), TRUE);
    gtk_header_bar_set_title(GTK_HEADER_BAR(header), "StudyAI");
    gtk_header_bar_set_subtitle(GTK_HEADER_BAR(header), "Powered by Mistral AI");
    gtk_window_set_titlebar(GTK_WINDOW(main_window), header);

    GtkWidget *theme_btn = gtk_button_new_with_label("🌙");
    gtk_widget_set_tooltip_text(theme_btn, "Toggle Theme");
    g_signal_connect(theme_btn, "clicked", G_CALLBACK(on_toggle_theme), NULL);
    gtk_header_bar_pack_end(GTK_HEADER_BAR(header), theme_btn);

    stack = gtk_stack_new();
    gtk_stack_set_transition_type(GTK_STACK(stack), GTK_STACK_TRANSITION_TYPE_CROSSFADE);
    gtk_stack_set_transition_duration(GTK_STACK(stack), 400);
    gtk_box_pack_start(GTK_BOX(main_vbox), stack, TRUE, TRUE, 0);

    // Start View
    GtkWidget *start_vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 30);
    gtk_widget_set_valign(start_vbox, GTK_ALIGN_CENTER);
    gtk_widget_set_halign(start_vbox, GTK_ALIGN_CENTER);
    
    // Title - plain text, no background box
    GtkWidget *title_label = gtk_label_new(NULL);
    gtk_label_set_markup(GTK_LABEL(title_label), "<b>Study\nAI</b>");
    gtk_label_set_justify(GTK_LABEL(title_label), GTK_JUSTIFY_CENTER);
    gtk_style_context_add_class(gtk_widget_get_style_context(title_label), "title");
    
    // Random greeting subtitle
    const char *greeting = greetings[rand() % NUM_GREETINGS];
    GtkWidget *subtitle_label = gtk_label_new(greeting);
    gtk_style_context_add_class(gtk_widget_get_style_context(subtitle_label), "subtitle");
    gtk_label_set_justify(GTK_LABEL(subtitle_label), GTK_JUSTIFY_CENTER);

    gtk_box_pack_start(GTK_BOX(start_vbox), title_label, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(start_vbox), subtitle_label, FALSE, FALSE, 0);

    gtk_stack_add_named(GTK_STACK(stack), start_vbox, "start_view");

    // Chat View
    scrolled_window = gtk_scrolled_window_new(NULL, NULL);
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrolled_window), GTK_POLICY_NEVER, GTK_POLICY_AUTOMATIC);
    
    chat_list_box = gtk_list_box_new();
    gtk_list_box_set_selection_mode(GTK_LIST_BOX(chat_list_box), GTK_SELECTION_NONE);
    gtk_container_add(GTK_CONTAINER(scrolled_window), chat_list_box);
    
    gtk_stack_add_named(GTK_STACK(stack), scrolled_window, "chat_view");

    // Input Area
    GtkWidget *input_area = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 12);
    gtk_widget_set_margin_start(input_area, 20);
    gtk_widget_set_margin_end(input_area, 20);
    gtk_widget_set_margin_bottom(input_area, 20);
    gtk_widget_set_margin_top(input_area, 15);

    prompt_entry = gtk_entry_new();
    gtk_entry_set_placeholder_text(GTK_ENTRY(prompt_entry), "Ask me anything...");
    g_signal_connect(prompt_entry, "activate", G_CALLBACK(on_send_clicked), NULL);
    
    GtkWidget *send_btn = gtk_button_new_with_label("Send");
    gtk_style_context_add_class(gtk_widget_get_style_context(send_btn), "send-btn");
    g_signal_connect(send_btn, "clicked", G_CALLBACK(on_send_clicked), NULL);

    gtk_box_pack_start(GTK_BOX(input_area), prompt_entry, TRUE, TRUE, 0);
    gtk_box_pack_start(GTK_BOX(input_area), send_btn, FALSE, FALSE, 0);

    gtk_box_pack_end(GTK_BOX(main_vbox), input_area, FALSE, FALSE, 0);
    
    // Context info
    context_label = gtk_label_new("Context: 0/32000 tokens (0%)");
    gtk_style_context_add_class(gtk_widget_get_style_context(context_label), "context-info");
    gtk_widget_set_margin_start(context_label, 20);
    gtk_widget_set_margin_end(context_label, 20);
    gtk_widget_set_margin_bottom(context_label, 8);
    gtk_box_pack_end(GTK_BOX(main_vbox), context_label, FALSE, FALSE, 0);

    set_theme(0);
    gtk_widget_show_all(main_window);
    gtk_main();

    return 0;
}
